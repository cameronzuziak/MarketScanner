from ftplib import FTP

exportList = []


class DataParser:

    def get_list(self):
        return exportList

    def __init__(self, update=True):
        filenames = {
            "nasdaqlisted": "stocks/nasdaqlisted.txt"
        }

        if update == True:
            self.ftp = FTP("ftp.nasdaqtrader.com")
            self.ftp.login()
            self.ftp.getwelcome()
            self.ftp.cwd("SymbolDirectory")

            for filename, filepath in filenames.items():
                self.ftp.retrbinary("RETR " + filename + ".txt", open(filepath, 'wb').write)

        listed_stocks = open("stocks/cleanedlist.txt", 'w')
        for filename, filepath in filenames.items():
            with open(filepath, "r") as file_reader:
                for i, line in enumerate(file_reader, 0):
                    if i == 0:
                        continue
                    line = line.strip().split("|")
                    if line[0] == "" or line[1] == "" or line[6] == 'Y':
                        continue
                    listed_stocks.write(line[0] + ",")
                    global exportList
                    exportList.append(line[0])
                    listed_stocks.write(line[0] + "|" + line[1] + "\n")
