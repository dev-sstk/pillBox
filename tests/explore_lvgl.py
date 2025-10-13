import lvgl as lv
import ujson
import gc

def is_class(obj):
    """클래스 판별 (MicroPython용)"""
    return type(obj).__name__ == "type"

def is_module(obj):
    """모듈 판별 (MicroPython용)"""
    return type(obj).__name__ == "module"

def explore_to_file(obj, f, parent_path="lv", visited=None):
    """
    각 노드를 탐색하면서 파일에 바로 기록
    - obj: 탐색할 객체
    - f: 파일 객체
    - parent_path: 부모 경로 문자열 ("lv.Button" 형태)
    - visited: 순환 참조 방지 집합
    """
    if visited is None:
        visited = set()

    obj_id = id(obj)
    if obj_id in visited:
        return
    visited.add(obj_id)

    try:
        members = dir(obj)
    except Exception as e:
        # 에러 노드 기록
        f.write(ujson.dumps({
            "path": parent_path,
            "error": str(e)
        }) + "\n")
        return

    for name in members:
        try:
            attr = getattr(obj, name)
            tname = type(attr).__name__
            path = parent_path + "." + name  # 전체 경로

            # 현재 노드 기록
            node = {
                "path": path,
                "type": tname
            }
            f.write(ujson.dumps(node) + "\n")

            # 진행 상황 출력
            if is_class(attr) or is_module(attr):
                print("탐색 중:", path)
                explore_to_file(attr, f, parent_path=path, visited=visited)

            gc.collect()  # 메모리 확보

        except Exception as e:
            f.write(ujson.dumps({
                "path": parent_path + "." + name,
                "error": str(e)
            }) + "\n")


def main():
    print("LVGL 구조 탐색 시작...")
    with open("lvgl_structure.jsonl", "w") as f:
        explore_to_file(lv, f, parent_path="lv")
    print("완료! JSONL 저장됨: lvgl_structure.jsonl")
