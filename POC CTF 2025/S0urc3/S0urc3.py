arr = [71,105,102,104,88,120,107,108,49,54,103,55,52,45,104,110,51,98,60,58,52,98,103,106,55,97,105,110,50,96,55,59,99,49,60,61,56,54,130]

ans = []
for i in range(len(arr)):
    num  = i % 4
    if num == 0:
        ans.append(arr[i] ^ 0x01)
    elif num == 1:
        ans.append(arr[i] + 3)
    elif num == 2:
        ans.append(arr[i] - 5)
    elif num == 3:
        ans.append(arr[i] ^ 0x0F)

for i in range(len(ans)):
    ans[i] = chr(ans[i])

print("Flag : " + "".join(ans))