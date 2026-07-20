#!/bin/bash
# Usage: ./loop.sh [options]
# Options:
#   -m, --mode <plan|build>      Mode (default: build)
#   -n, --max <number>           Max iterations, 0 for unlimited (default: 0)
#   -s, --stop <string>          Completion promise - stop when this string appears in output
#   -p, --prompt <file>          Custom prompt file (overrides mode default)
#   -h, --help                   Show this help message
#
# Examples:
#   ./loop.sh                                    # Build mode, unlimited
#   ./loop.sh -m plan                            # Plan mode, unlimited
#   ./loop.sh -m plan -n 5                       # Plan mode, max 5 iterations
#   ./loop.sh -n 10 -s "DONE"                    # Build mode, max 10 or stop on "DONE"
#   ./loop.sh --mode plan                        # Plan mode,
#   ./loop.sh -p custom_prompt.md -n 3           # Custom prompt file

# Defaults
MODE="build"
MAX_ITERATIONS=0
COMPLETION_PROMISE="DONE"
PROMPT_FILE=""

# Parse named arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--mode)
            MODE="$2"
            shift 2
            ;;
        -n|--max)
            MAX_ITERATIONS="$2"
            shift 2
            ;;
        -s|--stop)
            COMPLETION_PROMISE="$2"
            shift 2
            ;;
        -p|--prompt)
            PROMPT_FILE="$2"
            shift 2
            ;;
        -h|--help)
            head -n 16 "$0" | tail -n 15
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage"
            exit 1
            ;;
    esac
done

# Set default prompt file based on mode if not specified
if [ -z "$PROMPT_FILE" ]; then
    case "$MODE" in
        plan)
            PROMPT_FILE="PROMPT_plan.md"
            ;;
        build)
            PROMPT_FILE="PROMPT_build.md"
            ;;
        review)
            PROMPT_FILE="PROMPT_review.md"
            ;;
        *)
            echo "Unknown mode: $MODE"
            echo "Valid modes: plan, build, review"
            exit 1
            ;;
    esac
fi

ITERATION=0
CURRENT_BRANCH=$(git branch --show-current)

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Mode:   $MODE"
echo "Prompt: $PROMPT_FILE"
echo "Branch: $CURRENT_BRANCH"
[ -n "$COMPLETION_PROMISE" ] && echo "Stop:   '$COMPLETION_PROMISE'"
[ $MAX_ITERATIONS -gt 0 ] && echo "Max:    $MAX_ITERATIONS iterations"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verify prompt file exists
if [ ! -f "$PROMPT_FILE" ]; then
    echo "Error: $PROMPT_FILE not found"
    exit 1
fi

while true; do
    if [ $MAX_ITERATIONS -gt 0 ] && [ $ITERATION -ge $MAX_ITERATIONS ]; then
        echo "Reached max iterations: $MAX_ITERATIONS"
        break
    fi

    # Run Ralph iteration with selected prompt
    # Read the prompt file and pass to Claude Code
    PROMPT_CONTENT=$(cat "$PROMPT_FILE")
    #PROMPT_CONTENT="Update the readme file to say the author is Ralph. Output <promise>DONE</promise> when complete."
    echo "$PROMPT_CONTENT"

    # Capture output while still displaying it.
    # Claude Code headless flags:
    #   -p / --print                     run non-interactively (prompt in, result out, then exit)
    #   --model opus                     use latest Opus (or a full id like claude-opus-4-8)
    #   --dangerously-skip-permissions   no approval prompts (== Copilot's --allow-all-tools).
    #                                    Won't run as root; only use on a repo you can afford to
    #                                    let an agent modify + push. Optional: add --max-turns N
    #                                    to cap agentic turns (and cost) per iteration.
    # Feed the prompt in via stdin (robust on Windows/Git Bash, where a long -p
    # argument and a `< /dev/null` redirect don't survive the native claude shim).
    # `claude -p` here is just the print-mode switch; the prompt comes from stdin.
    OUTPUT=$(printf '%s\n' "$PROMPT_CONTENT" | claude -p \
        --model opus \
        --dangerously-skip-permissions \
        2>&1 | tee /dev/stderr)

    # Push changes after each iteration
    git push origin "$CURRENT_BRANCH" || {
        echo "Failed to push. Creating remote branch..."
        git push -u origin "$CURRENT_BRANCH"
    }

   # Check for completion promise in output (I always set this)
    if [ -n "$COMPLETION_PROMISE" ] && echo "$OUTPUT" | grep -q "$COMPLETION_PROMISE"; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "✓ Completion promise found: '$COMPLETION_PROMISE'"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        break
    fi

    ITERATION=$((ITERATION + 1))
    echo -e "\n\n======================== LOOP $ITERATION ========================\n"
done