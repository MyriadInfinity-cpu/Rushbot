import random



class DiceRoller:
    @staticmethod
    def roll_d10_crit():
        output_text = ""
        output_sum = -1

        result = random.randint(1, 10)

        output_text = str(result)
        output_sum = result
        print("\tRolling die: got a "+str(result))
        if result == 1:
            result = random.randint(1, 10)
            output_text += "-"+str(result)
            output_sum = output_sum-result
        elif result == 10:
            result = random.randint(1, 10)
            output_text += "+"+str(result)
            output_sum = output_sum+result
        #return ("9", 9)
        return (output_text, output_sum)

class OneDeal:
    type = ""
    quantity = -1
    price = -1
    category = ""
    output_text = ""
    output_sum = 0
    output_value = 0

    output_sale_price = 0
    output_sale_cost = 0

    @staticmethod            #  0              1     2                  3      4
    def helper(input_string): # sell (if yes), type, quantity (if any), price, category
        parts = "Error."
        print(f"inside helper with {input_string}")
        if input_string.startswith("buy"):
            parts = input_string[len("buy"):].strip().split(" ")
            input_string = input_string[len("buy"):]
        elif input_string.startswith("sell"):
            parts = input_string[len("sell"):].strip().split(" ")
        else:
            parts = input_string.split(" ")

        print(parts)
        print(input_string)
        if input_string.startswith("6f5"):
            print(f"6f5 deal found with {parts}")
            return OneDeal("6f5", int(parts[1]), parts[2], 1)
        elif input_string.startswith("sell"):
            print(f"sell deal found with {parts}")
            return OneDeal(f"sell{parts[0]}", int(parts[2]), parts[3], int(parts[1]))
        elif input_string.startswith("delay"):
            print(f"delay deal found with {parts}")
            return OneDeal("delay", int(parts[1]), parts[2], 1)
        elif input_string.strip().startswith("10%"):
            print(f"10% deal found with {parts}")
            return OneDeal("10%", int(parts[2]), parts[3], int(parts[1]))
        elif input_string.strip().startswith("20%"):
            print(f"20% deal found with {parts}")
            return OneDeal("20%", int(parts[2]), parts[3], int(parts[1]))
        else:
            return "error"

    def __init__(self, type, price, category, quantity=1):
        # Quantity of more than 1 means we run it more than once.
        self.type = type
        self.quantity = quantity
        self.price = price
        self.category = category
        self.output_text = f"{self.type}. Quantity: {quantity}, Price: {price}, Category: {category}\n"
        print(self.output_text)

    def roll_it(self, modifier):
        for i in range(self.quantity):
            single = OneTrade(self.type, self.price, self.category, modifier)
            if self.type.startswith("sell"):
                single.roll()
                t = single.ret()
                self.output_text += str(i+1) + ". " + t[0] + "\n"
                self.output_sale_cost += t[1] # stores the cost of sold goods
                self.output_sale_price += t[2] # stores the value of sold goods
            else:
                single.roll()
                t = single.ret()
                self.output_text += str(i+1) + ". " + t[0] + "\n"
                self.output_sum += t[1]
                self.output_value += t[2]
        self.output_text += f"Total cost: {self.output_sum}, Total value: {self.output_value}\n"
        if self.output_sale_price != 0:
            self.output_text += f"Sale price: {self.output_sale_price}, Sale cost: {self.output_sale_cost}\n"
    def ret(self):
        return (self.output_text, self.output_sum, self.output_value, self.output_sale_price, self.output_sale_cost)

class OneTrade:
    type = ""
    price = -1
    category = ""
    modifier = -1
    success = False
    output_text = ""
    output_cost = -1
    output_value = -1
    def __init__(self, type, price, category, modifier):
        self.type = type
        self.price = price
        self.category = category
        self.modifier = modifier
    def roll(self):
        player = DiceRoller.roll_d10_crit()
        opp = DiceRoller.roll_d10_crit()
        print(f"opp rolled {opp[0]}/{opp[1]}, player rolled{player[0]}/{player[1]}")
        print(f"category is{lookup(self.category)}")
        if (player[1]+self.modifier) > (opp[1]+lookup(self.category)):
            self.success = True
            if self.type == "10%":
                self.output_cost = int(self.price * 0.9)
                self.output_value = self.price
            elif self.type == "20%":
                self.output_cost = int(self.price * 0.8)
                self.output_value = self.price
            elif self.type == "6f5":
                self.output_cost = self.price*5
                self.output_value = self.price*(6)
            elif self.type == "sell10%":
                self.output_cost = self.price
                self.output_value = int(self.price * 1.1)
            elif self.type == "sell20%":
                self.output_cost = self.price
                self.output_value = int(self.price * 1.2)
            else:
                self.output_cost = self.price
        else:
            if self.type == "6f5":
                self.output_cost = self.price*5
                self.output_value = self.price*5
            else:
                self.success = False
                self.output_cost = self.price
                self.output_value = self.price
        self.output_text=f"You: `d10 ({player[0]}) + {self.modifier} = {player[1]+self.modifier}` vs. Opponent: `d10 ({opp[0]}) + {lookup(self.category)} = {opp[1]+lookup(self.category)}`"
        if self.success:
            self.output_text += " :white_check_mark:"
        else:
            self.output_text += " :no_entry:"
        return (self.output_text, self.output_cost, self.output_value)
    def ret(self):
        return (self.output_text, self.output_cost, self.output_value)

def lookup(category):
    if category == "Cheap":
        return 12
    elif category == "Everyday":
        return 12
    elif category == "Costly":
        return 12
    elif category == "Premium":
        return 12
    elif category == "Expensive":
        return 14
    elif category == "Very_Expensive":
        return 18
    elif category == "Luxury":
        return 20
    elif category == "Super_Luxury":
        return 22
    else:
        return -1
"""
test = OneTrade("10%", 250, "Expensive", 14)
test.roll()
print(test.ret())

print("\n")

test2 = OneDeal("10%", 250, "Expensive", 4)
test2.roll_it(14)
print(test2.ret())
print(test2.ret()[0])

print("\n")

test3 = OneDeal.helper("10% 2 100 Premium")
test3.roll_it(14)
print(test3.ret())
print(test3.ret()[0])
"""