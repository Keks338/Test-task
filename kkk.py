import argparse
import re
from collections import defaultdict
from typing import List, Dict

def parse_logs(logfile_paths: List[str]) -> Dict[str, Dict[str, int]]:
    log_pattern = re.compile(
        r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+\s+'
        r'(?P<level>DEBUG|INFO|WARNING|ERROR|CRITICAL)\s+'
        r'(?P<source>[a-zA-Z0-9_.]+):\s+(?P<message>.+)'
    )

    path_pattern = re.compile(r'(?P<path>/[^\s]*)|Internal Server Error: (?P<error_path>/[^\s]*)')

    handler_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for filepath in logfile_paths:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    match = log_pattern.search(line)
                    if match:
                        level = match.group('level')
                        message = match.group('message')

                        path_match = path_pattern.search(message)
                        if path_match:
                            path = path_match.group('path') or path_match.group('error_path')
                        else:
                            continue

                        handler_stats[path][level] += 1
        except FileNotFoundError:
            print(f"Файл не найден: {filepath}")

    return handler_stats

def generate_report(handler_stats: Dict[str, Dict[str, int]], output_file: str) -> None:
    levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    total_requests = sum(sum(counts.values()) for counts in handler_stats.values())
    total_per_level = {lvl: 0 for lvl in levels}

    report_lines: List[str] = []
    report_lines.append(f"Total requests: {total_requests}\n")
    report_lines.append("{:<30} {:>7} {:>7} {:>7} {:>7} {:>9}".format('HANDLER', *levels))
    report_lines.append("-" * 80)

    for path, counts in sorted(handler_stats.items()):
        row = [path.ljust(30)]
        for lvl in levels:
            value = counts.get(lvl, 0)
            row.append(f"{value:>7}")
            total_per_level[lvl] += value
        report_lines.append(" ".join(row))

    report_lines.append("-" * 80)
    total_row = [" " * 30] + [f"{total_per_level[lvl]:>7}" for lvl in levels]
    report_lines.append(" ".join(total_row))

    with open(output_file, 'w', encoding='utf-8') as f:
        for line in report_lines:
            f.write(line + '\n')

    print(f"Отчёт успешно сохранён в {output_file}")

def main() -> None:
    parser = argparse.ArgumentParser(description="Анализатор логов Django по handler'ам")
    parser.add_argument('--files', nargs='+', required=True, help="Список путей к лог-файлам Django")
    parser.add_argument('--output', required=True, help="Путь к выходному текстовому файлу отчёта")

    args = parser.parse_args()

    handler_stats = parse_logs(args.files)
    generate_report(handler_stats, args.output)

if __name__ == "__main__":
    main()
