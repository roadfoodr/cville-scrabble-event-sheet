default:
    @just --list

# Trigger a Render rebuild of cvillescrabble.club (pulls latest data from Google Sheets)
deploy:
    bash .claude/skills/add-scrabble-events/scripts/rebuild-site.sh
