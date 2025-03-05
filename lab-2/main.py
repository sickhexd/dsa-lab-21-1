#Задание 1.1 Работа с математическими операциями в Python

#Задание 1 
# x = int(input("Введите число: "))
# y = int(input("Введите число: "))
# z = int(input("Введите число: "))
# maxim = max(x,y,z)
# print(maxim)

#Задание 2
# mas = [] 
# for i in range(3):
#     x = int(input("Введите число: "))
#     if 1 <= x <= 50:
#         mas.append(x)
# print(sorted(mas))

# Задание 3
# mas = []
# m = int(input("Введите число: "))
# for i in range(1,11):
#     mas.append(m*i)
# print(mas)

# Задание 4
# x = input("Введите числа: ")
# split_value = []
# tmp = ''
# for c in x:
#     if c == ' ':
#         split_value.append(tmp)
#         tmp = ''
#     else:
#         tmp += c
# if tmp:
#     split_value.append(tmp)
# print(split_value) 
# i = 0
# sum=0
# while i < len(split_value): 
#     sum = sum + int(split_value[i])
#     i=i+1
# print(f"Сумма: {sum}, кол-во: {i}") 

# Задание 2.1 Работа со строками
# x = input("Введите предложение: ")
# split_value = []
# tmp = ''
# for c in x:
#     if c == ' ':
#         split_value.append(tmp)
#         tmp = ''
#     else:
#         tmp += c
# if tmp:
#     split_value.append(tmp)
# print(split_value)
# slov = ''
# d = 0
# for i in range(len(split_value)):
#     slov = split_value[i]
#     l = list(slov)
#     if l[0] == "m" or l[0] == "M":
#         d = d + 1
# print(f"Слова начинающиеся с m: {d}")

# Задание 3.1 Работа со списками
# x = input("Введите числа: ")
# split_value = []
# tmp = ''
# for c in x:
#     if c == ' ':
#         split_value.append(int(tmp))
#         tmp = ''
#     else:
#         tmp += c
# if tmp:
#     split_value.append(int(tmp))
# print(f"Исходный массив: {split_value}")
# maxx = 0
# summ=0 
# for i in range(len(split_value)):
#     if maxx < split_value[i]:
#         maxx = split_value[i]
#     summ = summ + split_value[i]
# avg = summ / len(split_value) 
# print(f"Максимальный элемент: {maxx}")
# split_value.reverse()
# print(f"Перевернутый массив: {split_value}")
# split_value.reverse()
# for i in range(len(split_value)):
#     if split_value[i] == 0:
#         split_value[i] = avg
# print(f"Средние значения: {split_value}")