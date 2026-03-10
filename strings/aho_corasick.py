from __future__ import annotations

from collections import deque


class Automaton:
    '''
    初始化自动机
    先创建trie及其根节点，之后调用add_keyword将关键词的每个字符没有重复的加入进去，最后调用set_fail_transitions创建失配指针
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
    在添加关键词的时候用于检测某个字符是否已经作为节点存在
    遍历目前指向的位置的子节点，分析当前字符是否与这些子节点之一对应值相同
    '''
    def find_next_state(self, current_state: int, char: str) -> int | None:
        for state in self.adlist[current_state]["next_states"]:
            if char == self.adlist[state]["value"]:
                return state
        return None

    '''
    在初始化时被调用用于将关键词的字符不重复的添加进去并指明子节点关系
    '''
    def add_keyword(self, keyword: str) -> None:
        current_state = 0
        for character in keyword:
            '''
            调用find_next_state检测此字符是否已经已经被添加为子节点
            若不是，则添加为列表末尾新节点，如为此关键词第一个新节点，则子节点指向根节点，否则指向上一个节点
            关键词逐个字符处理完成后，在最后一个处理的字符处添加关键词字符串到output列表说明检测到这里的时候检测到了什么
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
    设置失配指针
    '''
    def set_fail_transitions(self) -> None:
        # 创建一个双端队列对象，并写上类型注解
        q: deque = deque()
        # 将根节点所有子节点位置添加到q右端，并配置这些子节点失配后转到根节点
        for node in self.adlist[0]["next_states"]:
            q.append(node)
            self.adlist[node]["fail_state"] = 0

        # 逐层遍历每层子节点的下一层子节点，直到队列清空
        while q:
            # 取出最先添加的子节点，将其子节点加入队列并添加它们失配后子节点为这个节点
            r = q.popleft()
            for child in self.adlist[r]["next_states"]:
                q.append(child)
                state = self.adlist[r]["fail_state"]
                # 
                while (
                    self.find_next_state(state, self.adlist[child]["value"]) is None
                    and state != 0
                ):
                    state = self.adlist[state]["fail_state"]
                self.adlist[child]["fail_state"] = self.find_next_state(
                    state, self.adlist[child]["value"]
                )
                if self.adlist[child]["fail_state"] is None:
                    self.adlist[child]["fail_state"] = 0
                self.adlist[child]["output"] = (
                    self.adlist[child]["output"]
                    + self.adlist[self.adlist[child]["fail_state"]]["output"]
                )

    '''
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
            while (
                self.find_next_state(current_state, string[i]) is None
                and current_state != 0
            ):
                current_state = self.adlist[current_state]["fail_state"]
            next_state = self.find_next_state(current_state, string[i])
            if next_state is None:
                current_state = 0
            else:
                current_state = next_state
                for key in self.adlist[current_state]["output"]:
                    if key not in result:
                        result[key] = []
                    result[key].append(i - len(key) + 1)
        return result


if __name__ == "__main__":
    import doctest

    doctest.testmod()
