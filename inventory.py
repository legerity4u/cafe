def read_file(fname):
    try:
        with open(fname, mode='r', encoding='utf-8') as f:
            tuples_list = []
            for line in f:
                parts = line.strip().split(',')
                result = []
                for i, part in enumerate(parts):
                    if i == 0:
                        result.append(part.strip('"'))
                    else:
                        result.append(int(part.strip()))
                tuples_list.append(tuple(result))
        return tuples_list
    except FileNotFoundError:
        print(f"File '{fname}' not found.")
        return []
    except Exception as e:
        print(f"Error: '{e}'")
        return []
    
    

