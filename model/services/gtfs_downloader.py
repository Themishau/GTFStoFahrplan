import argparse
from datetime import datetime
from pathlib import Path

import requests

VBB_GTFS_URL = "https://vbb.de/vbbgtfs"
VRR_PACKAGE_URL = (
    "https://opendata.ruhr/api/3/action/"
    "package_show?id=soll-fahrplandaten-vrr"
)
DEFAULT_TIMEOUT_SECONDS = 30


def _resolve_download_url(
        provider: str,
        session: requests.Session,
        timeout: int,
) -> str:
    if provider == "vbb":
        return VBB_GTFS_URL
    if provider != "vrr":
        raise ValueError(f"Unsupported GTFS provider: {provider!r}")

    response = session.get(VRR_PACKAGE_URL, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    if payload.get("success") is not True:
        raise RuntimeError("The VRR data catalog returned an unsuccessful response")

    resources = payload.get("result", {}).get("resources", [])
    downloads = [
        resource
        for resource in resources
        if resource.get("url")
           and (
                   str(resource.get("format", "")).lower() in {"gtfs", "zip"}
                   or str(resource["url"]).lower().endswith(".zip")
           )
    ]
    if not downloads:
        raise RuntimeError("The VRR data catalog contains no GTFS download")
    return str(downloads[-1]["url"])


def download_gtfs_feed(
        provider: str,
        output_directory: Path,
        *,
        timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> Path:
    """Download a supported provider's current GTFS feed."""
    provider = provider.lower()
    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)

    with requests.Session() as session:
        download_url = _resolve_download_url(provider, session, timeout)
        response = session.get(
            download_url,
            allow_redirects=True,
            stream=True,
            timeout=timeout,
        )
        response.raise_for_status()

        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        output_path = output_directory / f"{provider.upper()}_{timestamp}_GTFS.zip"
        with output_path.open("wb") as stream:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    stream.write(chunk)
    return output_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Download a GTFS feed")
    parser.add_argument("provider", choices=("vbb", "vrr"))
    parser.add_argument(
        "output_directory",
        nargs="?",
        type=Path,
        default=Path.cwd(),
    )
    arguments = parser.parse_args(argv)
    output_path = download_gtfs_feed(arguments.provider, arguments.output_directory)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
