"""Deeper-parsing coverage for Python / JS / TS / Java."""

from justokenmax import codeindex


def _syms(tmp_path, name, body):
    p = tmp_path / name
    p.write_text(body)
    lang = codeindex.LANGS[".{}".format(name.rsplit(".", 1)[1])]
    return {s["name"]: s for s in codeindex.parse_file(str(p), name, lang)}


# ---------------- Python ----------------
def test_python_annotations_and_return_type(tmp_path):
    s = _syms(tmp_path, "m.py",
              "def f(x: int, y: str = 'a') -> bool:\n    return True\n")
    assert s["f"]["sig"] == "def f(x: int, y: str) -> bool"


def test_python_decorator_and_async(tmp_path):
    body = ("class A:\n"
            "    @property\n"
            "    def val(self) -> int:\n        return 1\n"
            "    @staticmethod\n"
            "    async def go(n: int):\n        ...\n")
    s = _syms(tmp_path, "m.py", body)
    assert s["val"]["sig"] == "@property A.val(self) -> int"
    assert s["go"]["sig"] == "@staticmethod A.go(n: int)"


def test_python_module_constants(tmp_path):
    s = _syms(tmp_path, "m.py", "MAX: int = 5\nNAME = 'x'\nlower = 3\n")
    assert "MAX" in s and s["MAX"]["kind"] == "const"
    assert "NAME" in s            # ALL_CAPS assign captured
    assert "lower" not in s       # lowercase plain assign ignored


def test_python_class_bases(tmp_path):
    s = _syms(tmp_path, "m.py", "class B(A, X):\n    pass\n")
    assert s["B"]["sig"] == "class B(A, X)"


# ---------------- JS / TS ----------------
def test_js_class_methods_qualified(tmp_path):
    body = ("class Engine {\n"
            "  start(opts) {\n    return 1;\n  }\n"
            "  async stop() {}\n"
            "}\n")
    s = _syms(tmp_path, "a.js", body)
    assert s["Engine"]["kind"] == "class"
    assert s["start"]["kind"] == "method"
    assert s["start"]["sig"] == "Engine.start(opts)"
    assert s["stop"]["sig"] == "Engine.stop()"


def test_js_arrow_and_function_exports(tmp_path):
    body = ("export function render(props) {}\n"
            "export const handle = async (e) => {};\n")
    s = _syms(tmp_path, "a.js", body)
    assert s["render"]["sig"] == "render(props)"
    assert s["handle"]["sig"] == "handle(e)"


def test_ts_interface_type_enum(tmp_path):
    body = ("export interface User { id: number }\n"
            "export type ID = string;\n"
            "export enum Color { Red, Green }\n")
    s = _syms(tmp_path, "a.ts", body)
    assert s["User"]["kind"] == "interface"
    assert s["ID"]["kind"] == "type"
    assert s["Color"]["kind"] == "enum"


def test_js_control_flow_not_mistaken_for_method(tmp_path):
    body = ("class A {\n  run() {\n    if (x) {\n      go();\n    }\n  }\n}\n")
    s = _syms(tmp_path, "a.js", body)
    assert "if" not in s and "run" in s


# ---------------- Java ----------------
def test_java_methods_and_fields(tmp_path):
    body = ("public class Service {\n"
            "  private final int port;\n"
            "  public Service(int port) { this.port = port; }\n"
            "  public String handle(Request r) throws IOException {\n"
            "    return null;\n  }\n"
            "}\n")
    p = tmp_path / "S.java"
    p.write_text(body)
    syms = codeindex.parse_file(str(p), "S.java", "java")
    kinds = {(x["name"], x["kind"]) for x in syms}
    assert ("Service", "class") in kinds       # class
    assert ("Service", "method") in kinds      # constructor
    assert ("port", "field") in kinds
    handle = next(x for x in syms if x["name"] == "handle")
    assert handle["sig"] == "Service.handle(Request r): String"


def test_java_interface(tmp_path):
    s = _syms(tmp_path, "I.java", "public interface Repo {\n  void save();\n}\n")
    assert s["Repo"]["kind"] == "interface"
