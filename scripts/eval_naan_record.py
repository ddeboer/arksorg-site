"""
Script to evaluate a NAAN or NAAN plus shoulder record.

Given an NAAN record, this script will examine a cache of identifiers
for matching entries and attempt to resolve those identifiers using
the information contained in the NAAN record.
"""

import argparse
import asyncio
import dataclasses
import logging
import typing

import httpx

import naan_model
import rslv.lib_rslv

L = logging.getLogger(__name__)

@dataclasses.dataclass
class URL:
    target: str

    def __eq__(self, other:'URL') -> bool:
        if self.target == other.target:
            return True
        return False

    def __str__(self) -> str:
        return self.target


@dataclasses.dataclass
class HttpResponse:
    start_url: URL
    final_url: typing.Optional[URL] = None
    status_code: typing.Optional[int] = 0
    msecs: typing.Optional[int] = 0


async def follow_redirects_until(
        client:httpx.AsyncClient,
        url: str,
        headers: dict[str, str],
        stop_hosts:typing.Optional[list[str]]=None
    ) -> HttpResponse:
    if stop_hosts is None:
        stop_hosts = []
    visited = []
    result = HttpResponse(start_url=URL(url))
    try:
        visited.append(url)
        req = client.build_request("GET", url, headers=headers)
        last_response = None
        target_url = None
        while req is not None:
            try:
                L.debug("Send %s", req.url)
                response = await client.send(req)
            except Exception as e:
                L.error(f"client id %s url %s %s", id, req.url, e)
                break
            req = response.next_request
            if req is not None:
                _url = str(req.url)
                _is_local = False
                for prefix in stop_hosts:
                    if _url.startswith(prefix):
                        _is_local = True
                last_response = response
                target_url = _url
                if not _is_local:
                    break
                if _url in visited:
                    L.error("Cyclic redirect for %s", req.url)
                    raise ValueError("Redirect loop for %s", req.url)
                visited.append(_url)
                if not _is_local:
                    req = None
        L.debug("Finished last response %s", last_response.url)
        result.status = last_response.status_code,
        result.final_url = URL(target_url)
        result.msecs = int(last_response.elapsed.total_seconds()/1000.0)
        return result
    except Exception as e:
        L.error("Client id %s : %s", id, e)
    return result


async def do_work(naan, identifier):
    pid_parts = rslv.lib_rslv.split_identifier_string(identifier)
    url_template = ""
    if isinstance(naan.target[0], str):
        url_template = naan.target
    else:
        url_template = naan.target[0].url_template
    url = rslv.lib_rslv.unsplit_identifier_string(url_template, pid_parts)
    print(url)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("naan_record")
    parser.add_argument("identifier")
    args = parser.parse_args()
    with open(args.naan_record, "rt") as f:
        naan_str = f.read()
    naan = naan_model.naan_record_from_json(naan_str).as_public()
    asyncio.run(do_work(naan, args.identifier))


if __name__ == "__main__":
    main()