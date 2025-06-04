# This script runs the DeepWiki Markdown CLI to convert a DeepWiki page to Markdown format.
#!/bin/bash
# Usage: ./run.sh <DeepWiki URL> -d <depth>
# Example: python src/cli.py https://deepwiki.com/Fosowl/agenticSeek -d 2 -o docs
#          python src/cli.py https://deepwiki.com/Fosowl/agenticSeek -d 0
#          python src/cli.py https://deepwiki.com/qemu/qemu -d 0

# echo $1

python src/cli.py $1