#!/bin/bash
# Madness Interactive Mind Map Generator Launcher
# A convenient wrapper script for generating project mind maps

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🧠 Madness Interactive Mind Map Generator${NC}"
echo -e "${PURPLE}===========================================${NC}"
echo ""

# Default values
FORMAT="html"
OUTPUT=""
INTERACTIVE=""
DEPTH=3
OPEN_RESULT=""

# Function to show help
show_help() {
    echo -e "${CYAN}Usage:${NC}"
    echo "  $0 [options]"
    echo ""
    echo -e "${CYAN}Options:${NC}"
    echo "  -f, --format FORMAT    Output format: html, svg, dot, json (default: html)"
    echo "  -o, --output FILE      Output file (default: docs/mindmap.{format})"
    echo "  -i, --interactive      Add interactive features (HTML only)"
    echo "  -d, --depth N          Maximum scan depth (default: 3)"
    echo "  --open                 Open the generated file after creation"
    echo "  -h, --help             Show this help message"
    echo ""
    echo -e "${CYAN}Examples:${NC}"
    echo "  $0                               # Generate basic HTML mind map"
    echo "  $0 -i --open                     # Generate interactive HTML and open it"
    echo "  $0 -f svg -o my_mindmap.svg      # Generate SVG mind map"
    echo "  $0 -f json                       # Export data as JSON"
    echo ""
    echo -e "${CYAN}Quick commands:${NC}"
    echo "  $0 all                           # Generate all formats"
    echo "  $0 quick                         # Generate interactive HTML and open"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--format)
            FORMAT="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT="$2"
            shift 2
            ;;
        -i|--interactive)
            INTERACTIVE="--interactive"
            shift
            ;;
        -d|--depth)
            DEPTH="$2"
            shift 2
            ;;
        --open)
            OPEN_RESULT="true"
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        all)
            echo -e "${YELLOW}🚀 Generating all mind map formats...${NC}"
            make mindmap-all
            echo -e "${GREEN}✨ All formats generated in docs/ directory!${NC}"
            exit 0
            ;;
        quick)
            FORMAT="html"
            INTERACTIVE="--interactive"
            OPEN_RESULT="true"
            break
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Set default output if not provided
if [[ -z "$OUTPUT" ]]; then
    OUTPUT="docs/mindmap.${FORMAT}"
fi

# Create docs directory if it doesn't exist
mkdir -p docs

# Generate the mind map (fix the problematic line)
FORMAT_UPPER=$(echo "$FORMAT" | tr '[:lower:]' '[:upper:]')
echo -e "${BLUE}🎨 Generating ${FORMAT_UPPER} mind map...${NC}"
echo -e "${CYAN}   Format: ${FORMAT}${NC}"
echo -e "${CYAN}   Output: ${OUTPUT}${NC}"
echo -e "${CYAN}   Depth: ${DEPTH}${NC}"
[[ -n "$INTERACTIVE" ]] && echo -e "${CYAN}   Interactive: Yes${NC}"
echo ""

# Build the command
CMD="python3 scripts/mindmap_generator.py --format ${FORMAT} --output ${OUTPUT} --depth ${DEPTH}"
[[ -n "$INTERACTIVE" ]] && CMD="$CMD $INTERACTIVE"

# Execute the command
if $CMD; then
    echo ""
    echo -e "${GREEN}✨ Mind map generated successfully!${NC}"
    echo -e "${GREEN}   📁 File: ${OUTPUT}${NC}"
    
    # Get file size
    if [[ -f "$OUTPUT" ]]; then
        SIZE=$(du -h "$OUTPUT" | cut -f1)
        echo -e "${GREEN}   📊 Size: ${SIZE}${NC}"
    fi
    
    # Open the file if requested
    if [[ "$OPEN_RESULT" == "true" ]]; then
        echo -e "${YELLOW}🚀 Opening mind map...${NC}"
        case "$(uname -s)" in
            Darwin)  open "$OUTPUT" ;;
            Linux)   xdg-open "$OUTPUT" ;;
            CYGWIN*|MINGW*) start "$OUTPUT" ;;
            *) echo -e "${YELLOW}   Please open: ${OUTPUT}${NC}" ;;
        esac
    fi
    
    echo ""
    echo -e "${PURPLE}🧠 Enjoy exploring your Madness Interactive ecosystem!${NC}"
else
    echo -e "${RED}❌ Failed to generate mind map${NC}"
    exit 1
fi 
