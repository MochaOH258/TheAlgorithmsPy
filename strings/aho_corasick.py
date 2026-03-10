from __future__ import annotations

from collections import deque


class Automaton:
    '''
    初始化自动机：
    先创建 Trie 的根节点；
    再依次调用 add_keyword 将各关键词按字符插入 Trie，在当前前缀路径已存在时复用节点，不存在时新建节点；
    最后调用 set_fail_transitions 为各节点构造失配指针。
    '''
    def __init__(self, keywords: list[str]):
        self.adlist: list[dict] = []
        self.adlist.append(
            {"value": "", "next_states": [], "fail_state": 0, "output": []}
        )

        for keyword in keywords:
            self.add_keyword(keyword)
        self.set_fail_transitions()

    '''
    在当前状态的所有子节点中，查找是否存在字符值为 char 的子节点；
    若存在则返回其状态编号，否则返回 None。
    '''
    def find_next_state(self, current_state: int, char: str) -> int | None:
        for state in self.adlist[current_state]["next_states"]:
            if char == self.adlist[state]["value"]:
                return state
        return None

    '''
    在初始化时被调用，用于将一个关键词按字符逐步插入 Trie；
    对已存在的前缀路径直接复用，不存在的部分新建节点，并维护父子节点关系。
    '''
    def add_keyword(self, keyword: str) -> None:
        current_state = 0
        for character in keyword:
            '''
            调用 find_next_state 检查当前状态下是否已有字符为 character 的子节点；
            若没有，则创建新节点，并把该新节点编号加入当前状态的 next_states 中；
            若有，则沿已有节点继续向下。
            整个关键词处理完成后，把该关键词加入终止节点的 output，
            表示到达该状态时可以输出这个匹配结果。
            '''
            next_state = self.find_next_state(current_state, character)
            if next_state is None:
                self.adlist.append(
                    {
                        "value": character,
                        "next_states": [],
                        "fail_state": 0,
                        "output": [],
                    }
                )
                self.adlist[current_state]["next_states"].append(len(self.adlist) - 1)
                current_state = len(self.adlist) - 1
            else:
                current_state = next_state
        self.adlist[current_state]["output"].append(keyword)

    '''
    设置失配指针。
    '''
    def set_fail_transitions(self) -> None:
        # 创建一个双端队列对象，并写上类型注解
        q: deque = deque()
        # 将根节点的所有子节点加入队列，并将这些节点的失配指针设为根节点
        for node in self.adlist[0]["next_states"]:
            q.append(node)
            self.adlist[node]["fail_state"] = 0

        # 使用 BFS 按层遍历节点，直到队列清空
        while q:
            # 取出当前节点 r，并准备处理它的所有子节点
            r = q.popleft()
            for child in self.adlist[r]["next_states"]:
                q.append(child)
                state = self.adlist[r]["fail_state"]
                # 从父节点 r 的失配状态开始，检查是否存在字符值与当前 child 相同的转移；
                # 若不存在且当前状态不是根节点，则继续沿失配指针回退，
                # 直到找到可转移的状态或退回根节点
                while (
                    self.find_next_state(state, self.adlist[child]["value"]) is None
                    and state != 0
                ):
                    # 沿当前候选状态的失配指针继续回退
                    state = self.adlist[state]["fail_state"]
                # 回退结束后，将 child 的失配指针设为：
                # 从当前候选状态 state 出发，经 child 的字符值能到达的状态
                self.adlist[child]["fail_state"] = self.find_next_state(
                    state, self.adlist[child]["value"]
                )
                # 如果不存在这样的转移，则将失配指针设为根节点
                if self.adlist[child]["fail_state"] is None:
                    self.adlist[child]["fail_state"] = 0
                # 将失配指针所指状态的 output 合并到当前节点的 output 中，
                # 使较长模式串匹配成功时，也能同时输出其后缀对应的其他模式串
                self.adlist[child]["output"] = (
                    self.adlist[child]["output"]
                    + self.adlist[self.adlist[child]["fail_state"]]["output"]
                )

    '''
    检测。
    '''
    def search_in(self, string: str) -> dict[str, list[int]]:
        """
        >>> A = Automaton(["what", "hat", "ver", "er"])
        >>> A.search_in("whatever, err ... , wherever")
        {'what': [0], 'hat': [1], 'ver': [5, 25], 'er': [6, 10, 22, 26]}
        """
        result: dict = {}  # returns a dict with keywords and list of its occurrences
        current_state = 0
        for i in range(len(string)):
            # 扫描文本的每个字符；
            # 若当前状态下不存在该字符对应的转移，且当前状态不是根节点，
            # 就沿失配指针不断回退，直到找到可继续匹配的状态或退回根节点
            while (
                self.find_next_state(current_state, string[i]) is None
                and current_state != 0
            ):
                current_state = self.adlist[current_state]["fail_state"]
            # 回退结束后，尝试从当前状态读取当前字符：
            # 若仍无可用转移，则回到根状态；否则转移到对应的下一状态
            next_state = self.find_next_state(current_state, string[i])
            if next_state is None:
                current_state = 0
            else:
                current_state = next_state
                # 若当前状态的 output 非空，说明有关键词在当前位置结束；
                # 将这些关键词的起始位置加入结果字典 result
                for key in self.adlist[current_state]["output"]:
                    if key not in result:
                        result[key] = []
                    result[key].append(i - len(key) + 1)
        return result


if __name__ == "__main__":
    import doctest

    doctest.testmod()
