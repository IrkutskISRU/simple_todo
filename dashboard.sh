#!/usr/bin/env bash

reset

section() {
  local title="$1"
  echo ""
  local total_width=40
  local inner=" $title "
  local side_len=$(( (total_width - ${#inner}) / 2 ))
  (( side_len < 0 )) && side_len=0

  local line
  printf -v line '%*s' "$side_len" ''
  line=${line// /─}

  # серые линии + жёлтый заголовок (sublime‑style)
  printf '\033[38;5;240m%s \033[1;33m%s\033[38;5;240m %s\033[0m\n' "$line" "$title" "$line"
}

show_list() {
  local list_name="$1"
  todo list "$list_name" | sed -E \
    -e 's/^([0-9]+\.)/\x1b[38;5;250m\1\x1b[0m/' \
    -e 's/✅/\x1b[1;32m✅\x1b[0m/g' \
    -e 's/✔️/\x1b[1;37m✔️\x1b[0m/g'
}

section "ВЧЕРА"
show_list yesterday

section "ЕЖЕДНЕВНОЕ"
show_list daily

section "ТЕКУЩИЕ 3 ЗАДАЧИ"
show_list current

section "СЕГОДНЯ"
show_list today

section "ЗАВТРА"
show_list tomorrow

section "ПУЛ"
show_list pool

echo ""
