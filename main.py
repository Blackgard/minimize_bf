'''
    Лабораторная работа #1
    Задача: Минимизация Булевой функции.
    Подробнее:
    
    На вход программы подается описание системы булевых функций (БФ) в формате .PLA. 
    Возможно описание не полностью определенных БФ, допускаются противоречия (т.е. на одних 
    и тех же наборах значений входных переменных возможны различные значения функций). 
    
    Для данного задания нужно:
        1)	Выбрать номер функции, которая будет минимизироваться.
        2)	Используя принцип доминирования «1» доопределить выбранную функцию 
        до полностью определенной и удалить противоречия.
        3)	Для полученной функции применить одни из алгоритмов построения сокращенной ДНФ 
        (вариант 1 –алгоритм Квайна-МакКласки, вариант 2- алгоритм Блейка).
        4)	Результат (сокращенную ДНФ) записать в файл в формате .PLA.
        5)	Проверить работоспособность алгоритма на контрольных примерах (бенчмарки).
        6)	Оценить допустимый размер БФ. 

'''

import os
import fnmatch
import logging
import random 

from progress.bar import Bar

logger: logging.Logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)

BASE_FOLDER: str = os.path.abspath(os.path.dirname(__file__))
MES: dict = {
    'INPUT' : 'Введите номер функции (нумерация с 1) -> '
}

class MinimizerFunction:
    def __init__(self, countInput, countOutput, ilb, ob, rows, vectors):
        self.countInput = countInput
        self.countOutput = countOutput
        self.ilb = ilb
        self.ob = ob
        self.rows = rows
        self.vectors = vectors
        
        self.A = []
        self.B = []
        self.C = []
        
        print('Доступные функции', self.ob)

    def select_row(self, n):
        ''' Собирает нужные строки из двумерного массива'''
        A = []
        with Bar('Выбор строк: ', max = len(self.vectors)) as bar:
            for i in self.vectors:
                if i[1][n] == '1':
                    A.append(i[0])
                bar.next()
        self.A = A
        return A

    def add_vectors(self, A):
        '''Заменяет - на 0 и 1 тем самым увеличивает набор данных'''
        B = []
        with Bar('Добавляем вектора: ', max = len(A)) as bar:
            while A:
                temp = A.pop(0)
                if '-' in temp:
                    n = temp.find('-')
                    first = temp[:n] + '0' + temp[n + 1:]
                    second = temp[:n] + '1' + temp[n + 1:]
                    if '-' in first:
                        A.append(first)
                        A.append(second)
                    else:
                        B.append(first)
                        B.append(second)
                else:
                    B.append(temp)
                bar.next()
        self.B = B
        return B

    def create_func(self, dnf):
        size_dnf  = len(dnf)
        list1 = []
        list2 = []
        list3 = []
        mark  = [0]*size_dnf
        m     = 0
        
        with Bar('Склеивание векторов: ', max = size_dnf-1) as bar:
            # выполнения склеивания векторов
            for i in range(size_dnf-1):
                for j in range(i+1, size_dnf):
                    temp = self._glue(dnf[i], dnf[j])
                    if temp:
                        list1.append(temp)
                        mark[i] = 1
                        mark[j] = 1
                bar.next()
                    
        # делаем метку
        size2 = len(list1)
        mark2 = [0] * size2
        
        with Bar('Склеивание векторов 2 : ', max = size2-1) as bar:
            for i in range(size2-1):
                for j in range(i+1, size2):
                    if i != j and mark2[i] == 0:
                        if list1[i] == list1[j]:
                            mark2[j] = 1


        # добавляем разные элементы для нового списка
        with Bar('Добавление элементов: ', max = size2-1) as bar:
            for i in range(size2):
                if mark2[i] == 0:
                    list2.append(list1[i])

        # выбираем не учавствующие элементы
        with Bar('Добавление элементов: ', max = size_dnf) as bar:
            for i in range(size):
                if mark[i] == 0:
                    list3.append(dnf[i])
                    m += 1

        if m == size or size_dnf == 1:
            return list3
    
        return list3 + self.create_func(list2)

    def save_file(self, data, number):
        '''сохраняет результат в файл pla'''
        namesFun = self._create_normal_data(data)
        with open(f'dnf_{number}.plaC','w') as fout:
            print('.i', str(self.countInput), file=fout)
            print('.o', str(1), file=fout)
            print('.ilb', *self.ilb, file=fout)
            print('.ob', self.ob[number], file=fout)
            print('.p', len(data), file=fout)
            for i in data:
                print(i, 1, file=fout)
            print('.e', end='', file=fout)
        print(f'Был создан файл "dnf_{number}.plaC"')


    def _create_normal_data(self, A):
        '''формирует данные в читабельный список'''
        Names = self.ilb
        mDNF = []
        for vector in A:
            temp = ''
            for i in range(len(vector)):
                if vector[i] == '1':
                    temp += Names[i]+' '
                elif vector[i] == '0':
                    temp += 'not_'+Names[i]+' '
            mDNF.append(temp[:-1])
        return mDNF

    def _glue(self, vector1, vector2):
        '''метод осуществляет склеивание векторв'''
        newVector = ''
        count_glue = 0
        for i, j in zip(vector1, vector2):
            if i == j:
                newVector += i
            else:
                newVector += '-'
                count_glue += 1
        if count_glue-1:
            return None
        return newVector

class ReaderFile:
    """ Reader data from file"""
    def __init__(self, flag='r', **kwargs):
        """
        flag: 'r' (random) or 'nf' (file name)
        kwargs: fileName
        """
        self.flag = flag
        self.fileName = kwargs['fileName']
        self.data = ()
        
        if self.flag == 'r':
            pathFile = self.get_random_file()
            self.read_file(pathFile)
        elif self.flag == 'nf':
            self.read_file(self.fileName if self.fileName else None)
        else:
            logger.error('Flag is not correct!')
            raise 'Flag is not correct...'
    
    def toggle_flag(self):
        """ Set toggle value flag """
        if self.flag == 'r':
            self.flag = 'nf'
        elif self.flag == 'nf':
            self.flag = 'r'
        else:
            logger.error("Flag don't exsist!")
            
    def set_flag(self, flag: str) -> None:
        " Set flag value "
        self.flag = flag
        
    def set_file_name(self, fileName: str) -> None:
        " Set file name value "
        self.fileName = fileName
        
    def get_data(self) -> tuple:
        """ Return all data from readed file """
        return self.data
        
    def read_file(self, pathFile: str) -> tuple:
        ''' Read file and return turple data'''
        if not pathFile: raise "File not exsist!"
        
        with open(pathFile) as fin:
            ci = int(fin.readline().split()[1])
            co = int(fin.readline().split()[1])
            ilb = [i for i in fin.readline().split()[1:]]
            ob = [i for i in fin.readline().split()[1:]]
            r = int(fin.readline().split()[1])
            v = [[j for j in i.rstrip().split()] for i in fin.readlines()[:-1]]
        self.data = (ci, co, ilb, ob, r, v)
        
        return self.data

    def get_random_file(self) -> str:
        """ Return path on random file """
        
        plaForlder = os.path.join(BASE_FOLDER, 'pla')
        return os.path.join(plaForlder, random.choice(os.listdir(plaForlder)))

if __name__ == '__main__':
    reader: ReaderFile = ReaderFile('r', fileName = '')
    pla_data: tuple = reader.get_data()

    f = MinimizerFunction(*pla_data)

    number = int(input(MES['INPUT']))
    
    fd_row = f.select_row(number)
    dnf = f.add_vectors(fd_row)
    minim_func = f.create_func(dnf)
    
    f.save_file(minim_func, number)