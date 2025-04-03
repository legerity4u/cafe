from typing import List, Optional
import datetime
from dataclasses import dataclass
import inventory

@dataclass
class Topping:
    name: str
    price: int

    def __repr__(self) ->str:
        return f"{self.name:.<30}{self.price:.>10}"

@dataclass
class IceCreamFlavor:
    name: str
    price_per_ball: int
        
    def __repr__(self) -> str:
        return f"{self.name:.<30}{self.price_per_ball:.>10}"

@dataclass
class Container:
    type_name: str
    max_balls: int
    base_price: int = 0
        
    def __repr__(self) ->str:
        return f"{self.type_name:<25} (cap. {self.max_balls}){self.base_price:.>6}"

class Portion:
    def __init__(self, flavors: List[IceCreamFlavor], balls_count: List[int], container: Container, topping: Optional[Topping] = None):
        if len(balls_count) != len(flavors):
            raise ValueError("The quantity of scoops should correspond to the quantoty of flavors.")
        total_balls = sum(balls_count)
        if total_balls > container.max_balls:
            raise ValueError(f"Maximum {container.max_balls} scoops allowed for '{container.type_name}'.")
        self.flavors = flavors
        self.balls_count = balls_count
        self.container = container
        self.topping = topping

    @property
    def total_price(self) -> int:
        price = self.container.base_price
        price += sum(flavor.price_per_ball * count for flavor, count in zip(self.flavors, self.balls_count))
        if self.topping is not None:
            price += self.topping.price
        return price

    def __repr__(self) ->str:
        portion_text = f"{self.container.type_name}"
        portion_text += ", ".join(f" {count} x '{flavor.name}' " for flavor, count in zip(self.flavors, self.balls_count))
        if self.topping is not None:
            portion_text += f"with '{self.topping.name}'"
        portion_text += f"\tPrice:\t {self.total_price} RUB "
        return portion_text

class Order:
    _order_counter = 0
    
    def __init__(self):
        Order._order_counter += 1
        self.number=Order._order_counter
        self.portions =  []
        self.paid = False
        self.time_of_payment: Optional[datetime.datetime] = None

    @property
    def total_price(self) -> int:
        return sum(p.total_price for p in self.portions)

    def add_portion(self, portion: Portion):
        self.portions.append(portion)
        
    def pay(self):
        if not self.portions:
            raise ValueError("Can't pay for an empty order.")
        self.paid = True
        self.time_of_payment = datetime.datetime.now()

    def __repr__(self) ->str:
        if not self.portions:
            return f"Empty order."
        portions_text = [f"{idx+1}. {portion}" for idx, portion in enumerate(self.portions)]
        return "\n".join(portions_text) + f"\nTotal price: {self.total_price} RUB"

class Shift():
    _shift_counter = 0
    
    def __init__(self):
        Shift._shift_counter += 1
        self.number=Shift._shift_counter
        self.start_time: Optional[datetime.datetime] = None
        self.end_time: Optional[datetime.datetime] = None
        self.orders=[]
    
    @property
    def is_open(self) -> bool:
        return self.start_time is not None and self.end_time is None
    
    @property
    def revenue(self) -> int:
        return sum(order.total_price for order in self.orders)
    
    def open(self):
        if self.is_open:
            return
        if self.end_time is not None:
            raise ValueError("Can not reopen a closed shift.")
        self.start_time=datetime.datetime.now()
        print(f"Shift {self.number} has just been successfully opened at {self.start_time.strftime('%H:%M:%S')}.")
    
    def close(self):
        if not self.is_open:
            raise ValueError("Shift is not opened yet.")
        self.end_time=datetime.datetime.now()
        print(f"Shift {self.number} has just been successfully closed at {self.end_time.strftime('%H:%M:%S')}.")

    def add_order(self, order: Order):
        if not self.is_open:
            raise ValueError("Can't add an order to a closed shift.")
        order.pay()
        self.orders.append(order)
        print(f"Order {order.number} for {order.total_price} RUB was paid at {order.time_of_payment.strftime('%H:%M:%S')}.")

    def __repr__(self):
        parts = [
            f"Shift {self.number}",
            f"Start: {self.start_time.strftime('%H:%M:%S') if self.start_time else 'Not started'}",
            f"Status: {'Open' if self.is_open else 'Closed'}",
            f"Orders: {len(self.orders)}",
            f"Revenue: {self.revenue} RUB",
            ]
        if self.end_time:
            parts.insert(2,f"End: {self.end_time.strftime('%H:%M:%S')}")
        return "\n".join(parts)
class Menu():
    def __init__(self, flavors: List[IceCreamFlavor], toppings: List[Topping], containers: List[Container]):
        self.flavors = flavors
        self.toppings = toppings
        self.containers = containers
    
    def show(self):

        print("\nIce cream flavors (RUB/ball):")
        for i, flavor in enumerate(self.flavors, start=1):
            print(f"\t{i}. {flavor}")
        print("\nToppings (RUB):")
        for i, topping in enumerate(self.toppings, start=1):
            print(f"\t{i}. {topping}")
        print("\nCons or Cups (RUB):")
        for i, container in enumerate(self.containers, start=1):
            print(f"\t{i}. {container}")
        
class IceCreamParlor:
    def __init__(self):

        self.flavors = []
        filename = './data/icecream.txt'
        tuples_list = inventory.read_file(filename)
        if tuples_list:
            for tup in tuples_list:
                self.flavors.append(IceCreamFlavor(tup[0], tup[1]))
        
        self.topings = []
        filename = './data/topping.txt'
        tuples_list = inventory.read_file(filename)
        if tuples_list:
            for tup in tuples_list:
                self.topings.append(Topping(tup[0], tup[1]))
        
        self.containers = []
        filename = './data/container.txt'
        tuples_list = inventory.read_file(filename)
        if tuples_list:
            for tup in tuples_list:
                self.containers.append(Container(tup[0], tup[1], tup[2]))
        
        self.menu = Menu(self.flavors, self.topings, self.containers)
        self.shifts: List[Shift] = []
        self.current_shift: Optional[Shift] = None
        
    def print_welcome(self):
        welcome = "Welcome to our ice cream parlor!"
        border="-"*len(welcome)
        print(f"\n{border}\n{welcome}\n{border}")
        
    def create_portion(self) -> Optional[Portion]:
        print("\nCreating a new portion:")
        
        container = self._select_item(self.containers,"Select a container (number) or 'X' to cancel: ", "container")
        if container is None:
            return None
        flavors = []
        balls_count = []
        remaining_balls = container.max_balls
        
        while remaining_balls > 0:
            flavor = self._select_item(self.flavors, f"Select a flavor (number): ", "flavor")
            if flavor is None:
                if not flavors:
                    return None
                break
            max_possible = remaining_balls
            balls = self._get_valid_input(f"How many scoops (1-{max_possible})? ", 1, max_possible)
            flavors.append(flavor)
            balls_count.append(balls)
            remaining_balls -= balls
            
            if remaining_balls == 0:
                break
            if not self._get_yes_no_input(f"Add more flavors? (Y/n) "):
                break
        
        topping = None
        if self._get_yes_no_input("Add topping? (Y/n) "):
            topping = self._select_item(self.topings, "Select topping (number): ", "topping")
        
        return Portion(flavors, balls_count, container, topping)
        
    def _select_item(self, items: list, prompt: str, item_name: str) -> Optional[object]:
        while True:
            choice = input(prompt).strip().lower()
            if choice == 'x':
                return None
            try:
                index = int(choice) - 1
                if 0 <= index < len(items):
                    return items[index]
                print(f"Invalid {item_name} number. Please try again.")
            except ValueError:
                print(f"Please enter a valid number or 'X' to cancel.")
                
    def _get_valid_input(self, prompt: str, min_val: int, max_val: int) -> int:
        while True:
            try:
                value = int(input(prompt))
                if min_val <= value <= max_val:
                    return value
                print(f"Invalid input. Please enter a number between {min_val} and {max_val}.")
            except ValueError:
                print("Please enter a valid number.")
                
    def _get_yes_no_input(self, prompt: str) -> bool:
        while True:
            choice = input(prompt).strip().lower()
            if choice in ('y', 'yes', ''):
                return True
            elif choice in ('n', 'no'):
                return False
            else:
                print("Please enter 'Y' for yes or 'N' for no.")
                
    def create_order(self):
        if not self.current_shift or not self.current_shift.is_open:
            print("Please open a shift first.")
            return
        order = Order()
        
        while True:
            portion = self.create_portion()
            if portion:
                order.add_portion(portion)
                print(f"Added: {portion}")
            if not self._get_yes_no_input("Add another portion? (Y/n) "):
                break
        if order.portions:
            self.current_shift.add_order(order)
        else:
            print("Order canceled.")
            
 
    def run(self):
        self.print_welcome()
        self.menu.show()
        actions = {
            'M': ("Show menu", self.menu.show),
            'N': ("Open shift", self._open_shift),
            'O': ("New order", self.create_order),
            'C': ("Close shift", self._close_shift),
            'S': ("Total per shift", self._show_shift_summary),
            'D': ("Total per day", self._show_dayly_summary),
            'Q': ("Exit", self._quit),
        }
        
        while True:
            print("\n"+"-" * 40)
            for key, (desc, _) in actions.items():
                print(f"{key}: {desc}", end=' | ')
            print("")
            
            action = input("Choose action: ").strip().upper()
            if action in actions:
                actions[action][1]()
            else:
                print("Incorrect input. Please select the action from menu.")
    def _open_shift(self):
        if self.current_shift and self.current_shift.is_open:
            print(f"Shift {self.current_shift.number} is already opened.")
            return
        self.current_shift = Shift()
        self.current_shift.open()
        self.shifts.append(self.current_shift)
        
    def _close_shift(self):
        if not self.current_shift or not self.current_shift.is_open:
            print("No open shift to close.")
            return
        self.current_shift.close()
        print(self.current_shift)
        self.current_shift = None
            
    def _show_shift_summary(self):
        if not self.current_shift or not self.current_shift.is_open:
            print("No open shift.")
            return
        print(self.current_shift)
        
    def _show_dayly_summary(self):
        if not self.shifts:
            print("No shift today.")
            return
        total_revenue = sum(shift.revenue for shift in self.shifts)
        print(f"\n=== DAILY SUMMARY ===")
        print(f"Shifts: {len(self.shifts)}\n")
        print(f"\nTotal revenue: {total_revenue} RUB")
        for shift in self.shifts:
            print(f"\n{shift}")
        
    def _quit(self):
        if self.current_shift and self.current_shift.is_open:
            self._close_shift()
        if self.shifts:
            self._show_dayly_summary()
        print("\nThank you for visiting our ice cream parlor!")
        exit()

if __name__ == "__main__":
    parlor = IceCreamParlor()
    parlor.run()