#random bytearray
randomByteArray = bytearray('ABC', 'utf-8')
print('Before updation:', randomByteArray)

mv = memoryview(randomByteArray)

# update 1st index of mv to Z
mv[1] = 90
print('After updation:', randomByteArray)