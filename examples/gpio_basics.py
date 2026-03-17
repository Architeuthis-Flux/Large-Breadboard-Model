"""
Basic GPIO (General Purpose Input/Output) operations.
This example shows digital I/O, direction control, and pull resistors.
"""
oled_copy_print(True)

print("GPIO Basics Demo")

# Test GPIO pin 1
outputPin = GPIO_1
inputPin = GPIO_2
print("Testing GPIO pin " + str(outputPin))

# disconnect(outputPin, -1)
# disconnect(inputPin, -1)
nodes_clear()
connect(outputPin, 3)

# Set as output
gpio_set_dir(outputPin, True)  # True = OUTPUT
print("Set as output")

# Blink test
print("Blinking 2 times...")
for i in range(2):
    gpio_set(outputPin, True)   # HIGH
    print(str(outputPin) + " = HIGH")
    time.sleep(0.25)
    
    gpio_set(outputPin, False)  # LOW
    print(str(outputPin) + " = LOW")
    time.sleep(0.25)

# Set as input
gpio_set_dir(inputPin, INPUT)  # False = INPUT


connect(inputPin, 13)
time.sleep_ms(100)

print("Set as input")

# Test pull resistors
pulls = [0, 1, -1]  # None, Up, Down
pull_names = ["NONE", "PULLUP", "PULLDOWN"]

for i, pull in enumerate(pulls):
    gpio_set_pull(inputPin, pull)
    time.sleep_ms(100)
    state = gpio_get(inputPin)
    print("Pull " + pull_names[i] + ": " + str(state))
    time.sleep(0.5)


connect(3,13)

for i in range(5):
    gpio_set(outputPin, True)   # HIGH
    time.sleep_ms(100)
    state = gpio_get(inputPin)
    
    print("Output = HIGH \tInput = " + str(state))
    
    time.sleep(0.5)
    
    gpio_set(outputPin, False)  # LOW
    time.sleep_ms(100)
    state = gpio_get(inputPin)
    
    print("Output = LOW \tInput = " + str(state))
    
    time.sleep(0.5)


print("GPIO Basics complete!")
oled_copy_print(False)
