import os, re, fileinput


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def parseFile(filename):
    file = open(filename, "r")
    groups = []
    screptRes = r"^\s*m_Script[\s\S]* (-?\d*), guid: ([abcdef\d]{32}), [ \S]*$"
    idRes = r"^--- !u![ \S]*&(\d*)$"
    id = ""
    for line in file:
        matchesId = re.finditer(idRes, line)
        for matchNum, match in enumerate(matchesId, start=1):
            id = match.group(1)
        matchesScript = re.finditer(screptRes, line)
        for matchNum, match in enumerate(matchesScript, start=1):
            groups.append((id, match.group(1), match.group(2)))
    return groups


currentFiles = []
oldFiles = []
for root, dirs, files in os.walk("/home/amfitorin/projects/mymerge/MyMerge/Assets/"):
    for file in files:
        if file.endswith(".prefab") or file.endswith(".unity"):
            currentFiles.append(os.path.join(root, file))

for root, dirs, files in os.walk("/home/amfitorin/projects/mymerge_test/MyMerge/Assets/"):
    for file in files:
        if file.endswith(".prefab") or file.endswith(".unity"):
            oldFiles.append(os.path.join(root, file))

intersectFiles = intersection(currentFiles, [value.replace("mymerge_test", "mymerge") for value in oldFiles])
results = []
for file in [value.replace("mymerge", "mymerge_test") for value in intersectFiles]:
    parse = parseFile(file)
    parse2 = parseFile(file.replace("mymerge_test", "mymerge"))
    if len(parse) > 0:
        for id1, fileId1, guid1 in parse:
            for id2, fileId2, guid2 in parse2:
                if id1 == id2 and (fileId1 != fileId2 or guid1 != guid2):
                    group = (fileId2, fileId1, guid2, guid1)
                    if group not in results:
                        results.append(group)
                    break

pattern = "m_Script: {{fileID: {0}, guid: {1}, type: 3}}"
for file in currentFiles:
    with fileinput.FileInput(file, inplace=True, backup='.bak') as file1:
        for line in file1:
            replaced = False
            for group in results:
                text_to_search = pattern.format(group[0], group[2])
                replacement_text = pattern.format(group[1], group[3])
                if text_to_search in line:
                    print(line.replace(text_to_search, replacement_text), end='')
                    replaced = True
                    break
            if not replaced:
                print(line, end='')
