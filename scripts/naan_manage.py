"""
Script to update the resolver configuration with updates from the NAAN registry and the EZID NAAN list.

This script should be run any time there is an update to the NAAN registry.

1. Existing entries not in the registry are disabled
2. Config entries are added or updated if they already exist.
3. The config metadata is updated to match the tag of the NAAN registry
"""
import json
import logging
import logging.config
import os
import os.path
import re
import sys
import typing
import click
import httpx
import sqlalchemy
import sqlalchemy.exc

import rslv.lib_rslv.piddefine
import rslv.config

# Override the shoulder-list URL with the env var ARKSORG_EZID_SHOULDERS_URL
EZID_SHOULDERS_URL = os.environ.get("ARKSORG_EZID_SHOULDERS_URL", "https://ezid.cdlib.org/static/info/shoulder-list.txt")

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s %(name)s:%(levelname)s: %(message)s",
            "dateformat": "%Y-%m-%dT%H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "standard",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "": {
            "handlers": [
                "console",
            ],
            "level": "INFO",
            "propogate": False,
        },
    },
}

LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "WARN": logging.WARNING,
    "ERROR": logging.ERROR,
    "FATAL": logging.CRITICAL,
    "CRITICAL": logging.CRITICAL,
}


def get_logger():
    return logging.getLogger("naan_manage")

def create_configuration_folder():
    L = get_logger()
    dbstr = rslv.config.settings.db_connection_string
    data_path = dbstr[len("sqlite:///"):]
    data_folder = os.path.dirname(data_path)
    L.info("Using data path: %s", data_folder)
    if not os.path.exists(data_folder):
        os.makedirs(data_folder, exist_ok=True)
        L.info("Created data folder: %s", data_folder)

def load_ezid_shoulder_list(url:str) -> typing.List[dict]:
    # regexp to match entries in the shoulder-list output
    L = get_logger()
    re_ark = re.compile(
        r"\b(?P<PID>ark:/?(?P<prefix>[0-9]{5,10})\/(?P<value>\S+)?)",
        re.IGNORECASE | re.MULTILINE,
    )
    response = httpx.get(url)
    if response.status_code == 200:
        L.info("Shoulder list retrieved from %s", url)
        text = response.text
        result = re_ark.finditer(text)
        pids = []
        for row in result:
            pid = {
                "scheme": "ark",
                "prefix": row.group("prefix"),
                "value": "" if row.group("value") is None else row.group("value"),
            }
            pids.append(pid)
        return pids
    else:
        L.error("HTTP response status %s. Failed to retrieve shoulder list from %s", response.status_code, url)
    return []

def get_ezid_naans(url:str) -> typing.Set[str]:
    L = get_logger()
    ezid_shoulders = load_ezid_shoulder_list(url)
    ezid_naans = set()
    for pid in ezid_shoulders:
        naan = pid.get("prefix")
        if naan is not None:
            ezid_naans.add(naan)
    L.info("Loaded %s NAANs for EZID", len(ezid_naans))
    return ezid_naans


@click.group()
@click.pass_context
@click.option("-V", "--verbosity", default="ERROR", help="Logging level")
def main(ctx, verbosity):
    verbosity = verbosity.upper()
    logging_config["loggers"][""]["level"] = verbosity
    logging.config.dictConfig(logging_config)
    L = get_logger()
    ctx.ensure_object(dict)
    ctx.obj["engine"] = sqlalchemy.create_engine(
        rslv.config.settings.db_connection_string, pool_pre_ping=True
    )
    return 0

@main.command("init")
@click.pass_context
@click.argument("description")
def intialize(ctx, description):
    """
    Initialize the data store
    """
    L = get_logger()
    create_configuration_folder()
    rslv.lib_rslv.piddefine.create_database(ctx.obj["engine"], description)
    L.info("Data store initialized at: %s", rslv.config.settings.db_connection_string)


@main.command("naans")
@click.pass_context
@click.option(
    "-u",
    "--url",
    help="URL from which to retrieve public NAAN registry JSON.",
    default="https://cdluc3.github.io/naan_reg_public/naans_public.json",
)
@click.option(
    "-z",
    "--ezid-naans-url",
    help="URL from which to retrieve the EZID shoulder-list text",
    default=EZID_SHOULDERS_URL
)
def load_public_naans(ctx, url, ezid_naans_url):
    """
    Load NAAN definitions from the Public NAAN registry.

    Note that some NAAN registrants have targets associated with "shoulders" that
    have been registered with N2T and are not expressed in the NAAN registry.
    Gathering this information requires pulling from the legacy N2T prefixes
    list at https://n2t.net/e/n2t_full_prefixes.yaml and locating the records
    of type "shoulder".

    Args:
        ctx: context
        url: URL of the public NAANs JSON.
        ezid_naans: path to JSON list of NAANs managed by EZID
    Returns:

    """

    L = get_logger()
    ezid_naan_list = list(get_ezid_naans(ezid_naans_url))
    if len(ezid_naan_list) < 1:
        L.warning("No EZID NAAN list available from url: %s", ezid_naans_url)

    session = rslv.lib_rslv.piddefine.get_session(ctx.obj["engine"])
    try:
        definitions = rslv.lib_rslv.piddefine.PidDefinitionCatalog(session)
        L.debug("Loading NAAN JSON from: %s", url)
        response = httpx.get(url)
        if response.status_code != 200:
            L.error("Download failed. Response status code: %s", response.status_code)
            return
        try:
            data = response.json()
        except Exception as e:
            L.exception(e)
            return

        canonical = "ark:/{prefix}/{value}"
        try:
            # Add a base ark: scheme definition.
            entry = rslv.lib_rslv.piddefine.PidDefinition(
                scheme="ark",
                target="/.info/{pid}",
                canonical=canonical,
                synonym_for=None,
                properties={
                    "what": "ark",
                    "name": "Archival Resource Key",
                },
            )
            res = definitions.add_or_update(entry)
            if res["n_changes"] < 0:
                L.info("Added entry %s", res["uniq"])
            elif res["n_changes"] > 0:
                L.info("Updated entry %s with %s changes", res["uniq"], res["n_changes"])
            else:
                L.info("Existing entry %s no changes.", res["uniq"])
        except Exception as e:
            L.warning(e)
            pass
        for naan, record in data.items():
            naan = str(naan)
            L.debug("Loading %s", naan)
            properties = record
            target = record.get("target", None)
            if target is None:
                target = "/.info/{pid}"
            else:
                if naan in ezid_naan_list:
                    # Special case of a NAAN that is managed by EZID
                    # Need to override the target
                    L.info("EZID NAAN: %s", naan)
                    target = "https://ezid.cdlib.org/ark:/{prefix}/{value}"
                else:
                    L.debug("NAAN: %s", naan)
                    target = target.replace("$arkpid", "ark:/{prefix}/{value}")
            entry = rslv.lib_rslv.piddefine.PidDefinition(
                scheme="ark",
                prefix=naan,
                value=None,
                target=target,
                properties=properties,
                canonical=canonical,
                synonym_for=None,
            )
            L.debug("Saving entry for NAAN: %s", naan)
            res = definitions.add_or_update(entry)
            if res["n_changes"] < 0:
                L.info("Added entry %s", res["uniq"])
            elif res["n_changes"] > 0:
                L.info("Updated entry %s with %s changes", res["uniq"], res["n_changes"])
            else:
                L.debug("Existing entry %s no changes.", res["uniq"])
        definitions.refresh_metadata()
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main())