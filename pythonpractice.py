import sys

def yrto100():
	## Datetime! and user input.  How long until you are 100?  What year will it be?
	import datetime
	curyr = datetime.date.today().year

	name, year = raw_input('What is your name?'), 100 - int(raw_input('What is your current age?'))
	
	print ('Hello, %s.  You will be 100 in %d years, the year %d' % (name,  year, curyr + year))

def oddseven():
	##Mod functions!
	import math
	number, divisor = int(raw_input('What number are you thinking of?')), int(raw_input('the second?'))
	#Check odd or even
	if number%4 == 0:
		print('even by 4!')
	elif number%2 == 0:
		print('only by 2')
	else:
		print('odd')
		#check divisibility
	if number%divisor == 0:
		print('%d is divisible by %d' %(number, divisor))

def shortlist():
	#random numbers, listcomprehension, if/else
	import random

	inlist = random.sample(xrange(100), 10)
	number = int(raw_input('what number are you thinking of?'))
	newlist = [x for x in inlist if x < 5]
	
	if number in inlist:
		print('%d is in the list' % (number), inlist)
		if number in newlist:
			print('%d is  within bounds' % (number), newlist)
		else:
			print('%d is in the not within bounds' % (number), newlist)
	else:
		print('Your number is not in the list!', inlist)

def divisors():
	#list comprehension and modulo
	number = int(raw_input('what number are you thinking of?'))
	divisors = [x for x in range(1,number+1) if number%x == 0]
	print divisors

def listoverlap():
	import random
	#given two lists what overlap? working with sets!
	list1, list2 = set(random.sample( xrange(50), 20)), set(random.sample( xrange(50), 15))
	print list1, list2 
	print list1.intersection(list2)

def stringlist():
	word = raw_input('What word are you thinking of?')
	if word == word[::-1]:
		print'Palindrome!'
	else:
		print'no palindrome'
def evenlist():
	import random
	 
	print [x for x in random.sample(xrange(10000), 10) if x%2==0]

def rockpaperscissors():
	import random

	play = raw_input('What is your choice? Rock Paper or Scissors?')[0].lower()
	comp = random.choice(['s','r','p'])

	if play == comp:
		print 'You tie'
	elif play == 'p':
		if comp == 's':
			print('You lose')
		else: 
			print ('You win!')
	elif play == 's':
		if comp == 'r':
			print('You lose')
		else: 
			print ('You win!')
	elif play == 'r':
		if comp == 'p':
			print('You lose')
		else: 
			print ('You win!')
	print comp, play

def guessinggame():
	import random
	i = 1
	#num = [x for x in random.sample(xrange(10), 10)]
	target = random.randint(0, 10)

	guess = int(raw_input('Guess a number: '))
	play = raw_input('Want to play?')
	while guess != target and play != 'quit':
		if guess > target:
			print('Lower')
		else:
			print('Higher')

		guess = int(raw_input('Guess a number: '))
		
		i += 1
	print "%d was it. You took %d tries to guess %d" %(guess, i, target)

def listoverlap():
	import random
	# nonset = harder, need to check length?>
	list1, list2 = random.sample( xrange(50), 20), random.sample( xrange(50), 20)
	print ([x for x in list1 if x in list2])
	print list1
	print list2

def isprime():
	num = int(raw_input('Number:'))
	#case1: 0 or 1
	if num == 0 or num == 1:
		print('Not prime')
	#case2: Two
	elif num == 2:
		print( "prime number")
	#Case: others
	elif num > 2:
		for x in range(2, num):
			if num%x == 0:
				print('composite')
				break
		else:
			print('prime')

def divisors2(number):
	#list comprehension and modulo
	#number = int(raw_input('what number are you thinking of?'))
	# returns True if not prime
	divisors = [x for x in range(1,number+1) if number%x == 0]
	
	if len(divisors) > 2:
		return True
	else:
		return False
def isprime2():
	num = int(raw_input('Number, please:'))
	#case1: 0 or 1
	if num == 0 or num == 1:
		print('Not prime')
	#case2: Two
	elif num == 2:
		print( "prime number")
	#Case: otherwise:
	elif num > 2:
		if divisors2(num):
			print('%d is a composite' %(num))
		else:
			print('%d is a prime' %(num))

def startend():
	import random
	#givena list return only start and end
	list1 = random.sample(xrange(1, 30), 10)
	return list1, [list1[0], list1[-1]]

def fibonacci():
	#fb: sequence of numbers where next number in sequence is sum of previous two.
	#first 5: (1, 1,  2, 3, 4, 5 )
	number, start, end = (	int(raw_input('Number: ')),
							int(raw_input('Start: ')),
							int(raw_input('End: '))
							)
	
	a = start
	b = end
	fib = []
	evens = []

	while sum(evens) < number:

		fib.append(a)
		
		if a%2 == 0:
			evens.append(a)

		a, b = b, a+b
		
	#print fib, sum(fib)
	print sum(evens)

def dups():
	import numpy as np

	mylist = np.random.choice(50, 75, replace=True)

	#print mylist, len(mylist)
	print set(mylist), len(set(mylist))

def mirror():
	words = raw_input('What do you have to say?').split(' ')
	print(' '.join(words[::-1]))

def password():
	import random, string
	import numpy as np
	level = int(raw_input('How long do you want the password? '))
	pw = []
	while len(pw) < level:
		pw.append(random.choice(string.letters + string.digits + "@#$&*_-:;',.?/"))
	
	print ''.join(pw)

def cowsandbulls():
	import random, string

	numbers = ''.join([random.choice(string.digits)for x in range(4)])
	tries, score = 0, [0, 0]
	
	while score[0] != 4:
		score = [0,0]
		tries +=1
		guess = raw_input('What is your guess?')
		
		for i,x in enumerate(guess):
			if x == numbers[i]:
				score[0] +=1
			elif x in numbers:
				score[1] += 1
		print score, guess
	
	print('You took %d tries to guess %s' % (tries, numbers))

def elementsearch():
	print 'I hate my life currently'

if __name__ == '__main__':
	
	#practice functions
	
	#yrto100()
	#oddseven()
	#shortlist()
	#divisors()
	#listoverlap() #with set
	#stringlist()
	#evenlist()
	#while raw_input('Do you want to play?') == 'Yes': 
		#rockpaperscissors()
	#guessinggame()
	#listoverlap() #non set
	#isprime()
	#isprime2()
	#print(startend())
	#fibonacci()
	#dups()
	#mirror()
	#password()
	#cowsandbulls()
	elementsearch()