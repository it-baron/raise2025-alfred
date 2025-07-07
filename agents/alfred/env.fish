if not contains "$HOME/raise2025/alfred/agents/alfred" $PATH
    # Prepending path in case a system-installed binary needs to be overridden
    set -x PATH "$HOME/raise2025/alfred/agents/alfred" $PATH
end
