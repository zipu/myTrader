import os, json, re

class util(object):
    """
       Offers useful utility functions
    """

    @staticmethod
    def toList(str):
        return re.sub(r';*$', "", str).split(';')

    @staticmethod
    def toString(list):
        return (';').join(list)

    @staticmethod
    def toDict(string):
        return json.loads(string, encoding='utf8')

    @staticmethod
    def load(dest):
        current_dir = os.path.dirname(__file__)
        full_dir = os.path.join(current_dir, '../data/%s.json'%dest)
        if os.path.isfile(full_dir):
            with open('./data/%s.json'%(dest)) as file:
                try:
                    ret = json.load(file)
                    return ret
                except Exception:
                    return {}


    @staticmethod
    def toFile(dest, data, ftype='json'):
        
        if ftype=='json':
            #old_data = util.load(dest)
            with open('./data/%s.json'%(dest), 'w+', encoding='utf8') as file:
                try:
                    old_data = json.load(file)
                    old_data.update(data)
                    json.dump(old_data, file, ensure_ascii=False)
                except Exception:
                    json.dump(data, file, ensure_ascii=False)
                    file.close()
                    
        elif ftype=='csv':
            import csv
            with open('./data/%s.csv'%(dest), 'a', newline='') as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=',')
                for row in data:
                    csvwriter.writerow(row)