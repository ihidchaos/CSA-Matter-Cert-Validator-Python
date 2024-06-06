def add_colon_every_two_chars(input_str):
    # 将字符串按照两个字符一组分隔开
    split_str = [input_str[i:i + 2] for i in range(0, len(input_str), 2)]
    # 使用 ':' 连接分隔后的字符串
    result = ":".join(split_str)
    return result
