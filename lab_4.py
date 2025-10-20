import os

class TTasks:
    def matrixMethod(self, matrix: list[list]) -> int:
        counter = len(matrix)
        for row in matrix:
            for cell in row:
                if cell == 0 or cell == "" or cell is None:
                    counter -= 1
                    break
        return counter

    def stringMethod(self, string: str) -> list[int]:
        pluses = 0
        stars = 0
        for ch in string:
            if ch == "+":
                pluses += 1
            elif ch == "*":
                stars += 1
        return [pluses, stars]

    def fileMethod(self, fileRoot: str, target: str) -> list[str]:
        listOfStrings = []
        if not os.path.exists(fileRoot):
            raise FileNotFoundError(f"Test file not found: {fileRoot}")
        with open(fileRoot, 'r', encoding='utf-8') as file:
            for line in file:
                if target in line:
                    listOfStrings.append(line.rstrip("\n").rstrip("\r"))
        return listOfStrings

class FileSearcher:
    """
    Второй класс. Выполняет поиск ключевых слов в файлах и агрегирует результаты,
    используя методы класса TTasks для постобработки (например, подсчёт символов).
    """
    def __init__(self, tasks: TTasks):
        self.tasks = tasks

    def find_and_count(self, file_path: str, keyword: str) -> dict:
        """
        Находит строки с keyword в файле file_path и возвращает словарь:
        {
          'count': количество найденных строк,
          'lines': список найденных строк,
          'pluses_stars_counts': список результатов stringMethod для каждой найденной строки
        }
        """
        found = self.tasks.fileMethod(file_path, keyword)
        counts = [self.tasks.stringMethod(line) for line in found]
        return {
            'count': len(found),
            'lines': found,
            'pluses_stars_counts': counts
        }

    def aggregate_counts(self, file_paths: list[str], keyword: str) -> dict:
        """
        Проходит по списку файлов, выполняет find_and_count для каждого и агрегирует:
        {
          'total_files': n,
          'files_with_hits': k,
          'total_matches': m,
          'per_file': [{'file': path, 'count': c, 'counts': [...]}, ...]
        }
        """
        per_file = []
        total_matches = 0
        files_with_hits = 0
        for path in file_paths:
            try:
                res = self.find_and_count(path, keyword)
            except FileNotFoundError:
                per_file.append({'file': path, 'error': 'missing'})
                continue
            per_file.append({'file': path, 'count': res['count'], 'counts': res['pluses_stars_counts']})
            total_matches += res['count']
            if res['count'] > 0:
                files_with_hits += 1
        return {
            'total_files': len(file_paths),
            'files_with_hits': files_with_hits,
            'total_matches': total_matches,
            'per_file': per_file
        }

class TTasksTest:
    def __init__(self, tasks: TTasks, searcher: FileSearcher):
        self.tasks = tasks
        self.searcher = searcher
        self.log_lines: list[str] = []

    def _read_lines(self, path: str) -> list[str]:
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        with open(path, 'r', encoding='utf-8') as f:
            return [ln.rstrip("\n").rstrip("\r") for ln in f]

    def __matrixCompare(self, results: list[int], solutionPath: str = "Matrix solution.txt") -> str:
        try:
            sol_lines = self._read_lines(solutionPath)
        except FileNotFoundError:
            return f"Missing solution file: {solutionPath}"
        sol = []
        for ln in sol_lines:
            if ln.isdigit() or (ln and ln[0] == "-" and ln[1:].isdigit()):
                sol.append(int(ln))
            else:
                return f"Invalid solution line: {ln} in {solutionPath}"
        if len(sol) != len(results):
            return f"Length mismatch: expected {len(sol)}, got {len(results)}"
        errors = []
        for idx, (r, s) in enumerate(zip(results, sol), start=1):
            if r != s:
                errors.append(str(idx))
        return ",".join(errors) if errors else ""

    def __matrixTestMethod(self, testsPath: str = "Matrix tests.txt") -> str:
        try:
            lines = self._read_lines(testsPath)
        except FileNotFoundError:
            return f"Missing test file: {testsPath}"
        matrix = []
        results = []
        for ln in lines:
            if "-" in ln:
                results.append(self.tasks.matrixMethod(matrix))
                matrix = []
            else:
                parts = ln.split()
                row = []
                for p in parts:
                    if p.isdigit() or (p and p[0] == "-" and p[1:].isdigit()):
                        row.append(int(p))
                    elif p == "":
                        row.append("")
                    else:
                        row.append(p)
                matrix.append(row)
        if matrix:
            results.append(self.tasks.matrixMethod(matrix))
        return self.__matrixCompare(results)

    def __stringCompare(self, results: list[list[int]], solutionPath: str = "String solution.txt") -> str:
        try:
            sol_lines = self._read_lines(solutionPath)
        except FileNotFoundError:
            return f"Missing solution file: {solutionPath}"
        sol = []
        for ln in sol_lines:
            parts = ln.split()
            if len(parts) != 2:
                return f"Invalid solution format in {solutionPath}: {ln}"
            try:
                sol.append([int(parts[0]), int(parts[1])])
            except ValueError:
                return f"Invalid ints in solution file: {ln}"
        if len(sol) != len(results):
            return f"Length mismatch: expected {len(sol)}, got {len(results)}"
        errors = []
        for idx, (r, s) in enumerate(zip(results, sol), start=1):
            if r != s:
                errors.append(str(idx))
        return ",".join(errors) if errors else ""

    def __stringTestMethod(self, testsPath: str = "String tests.txt") -> str:
        try:
            lines = self._read_lines(testsPath)
        except FileNotFoundError:
            return f"Missing test file: {testsPath}"
        results = []
        for ln in lines:
            results.append(self.tasks.stringMethod(ln))
        return self.__stringCompare(results)

    def __fileCompare(self, solutionRoot: str, results: list[str]) -> bool:
        try:
            sol_lines = self._read_lines(solutionRoot)
        except FileNotFoundError:
            raise
        return sol_lines == results

    def __fileTestMethod(self) -> str:
        errors = []
        for i in range(1, 4):
            test_file = f"File test {i}.txt"
            sol_file = f"File solution {i}.txt"
            try:
                result = self.tasks.fileMethod(test_file, "break")
            except FileNotFoundError:
                errors.append(f"missing_test_{i}")
                continue
            try:
                ok = self.__fileCompare(sol_file, result)
            except FileNotFoundError:
                errors.append(f"missing_solution_{i}")
                continue
            if not ok:
                errors.append(str(i))
        return ",".join(errors) if errors else ""

    def __interactionTest(self, test_files: list[str], keyword: str = "break") -> str:
        """
        Тестирует взаимодействие: безопасный парсинг Interaction solution.txt и гибкая проверка агрегированных результатов.
        Формат Interaction solution.txt:
        первая строка: <label> <expected_total_matches>
        последующие строки (опционально): <file_path> <expected_count>
        """
        try:
            interaction_sol = self._read_lines("Interaction solution.txt")
        except FileNotFoundError:
            return "Missing solution file: Interaction solution.txt"

        agg = self.searcher.aggregate_counts(test_files, keyword)

        if not interaction_sol:
            return "Invalid interaction solution file"

        # Разбор заголовка; допускаем дополнительные метки, берём последнее поле как число
        header_parts = interaction_sol[0].strip().split()
        if len(header_parts) < 1:
            return "Invalid header in interaction solution"
        try:
            expected_total_matches = int(header_parts[-1])
        except Exception:
            return "Invalid total matches value in interaction solution"

        if expected_total_matches != agg.get('total_matches', 0):
            return f"total_matches_mismatch: expected {expected_total_matches}, got {agg.get('total_matches', 0)}"

        # Разбор последующих строк; используем split(maxsplit=1) чтобы корректно поддерживать имена файлов с пробелами
        expected_per_file = []
        for line in interaction_sol[1:]:
            line = line.strip()
            if not line:
                continue
            parts = line.split(maxsplit=1)
            if len(parts) == 1:
                # если указано только число, считаем это глобальным несоответствием формата
                return f"Invalid line in interaction solution: {line}"
            # parts[0] может быть именем файла или меткой; пытаемся извлечь имя и число
            # Попробуем разделить на (path, count) по последнему пробелу
            try:
                # если строка в формате "File test 1.txt 2" — выделим путь и число
                path_part, count_part = parts[0], parts[1]
                # сюда возможны разные варианты: если parts[1] содержит число — ok
                # если path содержит пробелы, вариант выше не сработает; более надёжный способ:
                # разбиваем всю строку по пробелам справа
                rparts = line.rsplit(maxsplit=1)
                if len(rparts) != 2:
                    return f"Invalid line in interaction solution: {line}"
                path_expected = rparts[0]
                expected_count = int(rparts[1])
            except ValueError:
                return f"Invalid count in interaction solution line: {line}"
            expected_per_file.append((path_expected, expected_count))

        # Сопоставление ожидаемых per_file с агрегированными данными.
        # Разрешаем, чтобы expected_per_file мог быть короче или длиннее agg['per_file'].
        for idx, (path_expected, expected_count) in enumerate(expected_per_file):
            # Если в агрегированных данных нет записи для этого индекса, пытаемся найти по имени файла
            if idx < len(agg.get('per_file', [])):
                agg_entry = agg['per_file'][idx]
                agg_file = agg_entry.get('file')
                agg_count = agg_entry.get('count', 0)
                # Сначала проверяем совпадение по индексу; если имя отличается, ищем запись по имени файла
                if agg_file != path_expected:
                    # поиск по имени файла
                    found = next((e for e in agg['per_file'] if e.get('file') == path_expected), None)
                    if found is None:
                        return f"missing_agg_entry_for_{path_expected}"
                    agg_count = found.get('count', 0)
                if agg_count != expected_count:
                    return f"per_file_mismatch_at_{path_expected}: expected {expected_count}, got {agg_count}"
            else:
                # индекс вне диапазона — пробуем найти по имени
                found = next((e for e in agg.get('per_file', []) if e.get('file') == path_expected), None)
                if found is None:
                    return f"missing_agg_entry_for_{path_expected}"
                if found.get('count', 0) != expected_count:
                    return f"per_file_mismatch_at_{path_expected}: expected {expected_count}, got {found.get('count', 0)}"

        return ""  # пустая строка = нет ошибок


    def test(self):
        try:
            m_err = self.__matrixTestMethod()
        except Exception as e:
            m_err = f"EXCEPTION_MATRIX: {e}"
        self.log_lines.append("Matrix Tests errors: " + ("none" if m_err == "" else m_err))

        try:
            s_err = self.__stringTestMethod()
        except Exception as e:
            s_err = f"EXCEPTION_STRING: {e}"
        self.log_lines.append("String Tests errors: " + ("none" if s_err == "" else s_err))

        try:
            f_err = self.__fileTestMethod()
        except Exception as e:
            f_err = f"EXCEPTION_FILE: {e}"
        self.log_lines.append("File Tests errors: " + ("none" if f_err == "" else f_err))

        # Interaction test: проверка совместной работы TTasks и FileSearcher
        test_files = [f"File test {i}.txt" for i in range(1, 4)]
        try:
            inter_err = self.__interactionTest(test_files, keyword="break")
        except Exception as e:
            inter_err = f"EXCEPTION_INTERACTION: {e}"
        self.log_lines.append("Interaction Tests errors: " + ("none" if inter_err == "" else inter_err))

        overall_ok = all("none" in line for line in self.log_lines)
        header = "TEST RESULTS: PASS" if overall_ok else "TEST RESULTS: FAIL"
        output_lines = [header, "-" * len(header)] + self.log_lines

        for ln in output_lines:
            print(ln)

        with open("log.txt", "w", encoding="utf-8") as logf:
            for ln in output_lines:
                logf.write(ln + "\n")

        return overall_ok

if __name__ == "__main__":
    tasks = TTasks()
    searcher = FileSearcher(tasks)
    tester = TTasksTest(tasks, searcher)
    ok = tester.test()
    print("Exit status:", "0" if ok else "1")