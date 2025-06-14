#!/usr/bin/env bash
# build.sh for Next.js on Render

set -o errexit

# Install dependencies
npm ci

# Build the Next.js application
npm run build
