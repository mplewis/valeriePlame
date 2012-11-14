#!/usr/bin/python

def getListMedian(itemList):
	tempList = itemList[:]
	tempList.sort()
	if len(tempList) % 2 == 0:
		midHighIndex = len(tempList) / 2
		midLowIndex = midHighIndex - 1
		return (tempList[midHighIndex] + tempList[midLowIndex]) / 2
	else:
		return tempList[(len(tempList) - 1) / 2]

def withinPercent(percent, baseNum, testNum):
	percentDec = float(percent) / 100
	boundRange = baseNum * percentDec
	lowerBound = baseNum - boundRange
	upperBound = baseNum + boundRange
	withinUpper = testNum <= upperBound
	withinLower = testNum >= lowerBound
	return (withinUpper and withinLower)

# test cases for mathUtils
if __name__=='__main__':
	
	# getListMedian: unordered odd-length list, ordered even-length list with two medians to show average
	ls = [4, 2, 1, 5, 3, 7, 99]
	print getListMedian(ls) # returns 4
	lsEven = [1, 2, 3, 5, 7, 8, 9, 10]
	print getListMedian(lsEven) # returns (5 + 7) / 2 = 6

	# withinPercent: test cases to see if a number is within percentage bounds
	# 100 +/- 15% = 85 ... 115 (inclusive)
	number = 100
	percent = 15
	print withinPercent(percent, number, 110)
	print withinPercent(percent, number, 95.5)
	print withinPercent(percent, number, 115)
	print withinPercent(percent, number, 80)
	print withinPercent(percent, number, -30)