class Person:
    num_people = 0

    def __init__(self, name, salario):
        self.name = name
        self.salario = salario
        Person.num_people += 1

    @staticmethod
    def showNumberOfPeople():
        print "Total number of people: %d" % Person.num_people

    def sayHello(self):
        print "Hello, my name is %s." % self.name

    def payTax(self):
        if self.salario > 10000:
            print "I pay tax"
        else:
            print "I do not pay tax"

Person.showNumberOfPeople()
p1 = Person('Yago', 100000)
Person.showNumberOfPeople()
p2 = Person('Igor', 5000)
Person.showNumberOfPeople()
people = [p1, p2]
for person in people:
    person.sayHello()
    person.payTax()
