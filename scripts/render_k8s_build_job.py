#!/usr/bin/env python3

import argparse
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render the K8s image build job manifest.")
    parser.add_argument("--template", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--job-name", required=True)
    parser.add_argument("--namespace", required=True)
    parser.add_argument("--app-name", required=True)
    parser.add_argument("--build-service-account", required=True)
    parser.add_argument("--docker-config-secret", required=True)
    parser.add_argument("--github-repository", required=True)
    parser.add_argument("--git-sha", required=True)
    parser.add_argument("--image-name", required=True)
    parser.add_argument("--image-tag", required=True)
    parser.add_argument("--cache-repo", required=True)
    parser.add_argument("--dockerfile-path", required=True)
    parser.add_argument("--job-ttl-seconds", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    template = Path(args.template).read_text()
    replacements = {
        "JOB_NAME": args.job_name,
        "BUILD_NAMESPACE": args.namespace,
        "APP_NAME": args.app_name,
        "K8S_BUILD_SERVICE_ACCOUNT": args.build_service_account,
        "K8S_DOCKER_CONFIG_SECRET": args.docker_config_secret,
        "GITHUB_REPOSITORY": args.github_repository,
        "GITHUB_SHA": args.git_sha,
        "IMAGE_NAME": args.image_name,
        "IMAGE_TAG": args.image_tag,
        "CACHE_REPO": args.cache_repo,
        "DOCKERFILE_PATH": args.dockerfile_path,
        "K8S_JOB_TTL_SECONDS": args.job_ttl_seconds,
    }

    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)

    unresolved = sorted(set(re.findall(r"{{([A-Z0-9_]+)}}", rendered)))
    if unresolved:
        raise SystemExit(f"Unresolved placeholders: {', '.join(unresolved)}")

    Path(args.output).write_text(rendered)


if __name__ == "__main__":
    main()
