from functools import reduce
from random import random, randint
import click

class MarkovGenerator:
    def __init__(self, depth):
        self._frequencies_map = {}
        self._frequencies_list = {}
        self._depth = depth

    def scan_frequencies(self, text):
        """
        returns symbols self._frequencies_map
        """
        for i in range(self._depth, len(text)):
            string = text[i-self._depth : i]

            self._frequencies_map.setdefault(string, {})
            self._frequencies_map[string].setdefault(text[i], 0)
            self._frequencies_map[string][text[i]] += 1


        for (string, string_freq) in self._frequencies_map.items():
            self._frequencies_list[string] = sorted(string_freq.items(),
                                                    key=lambda tup: tup[1],
                                                    reverse=True)

            normalizer = reduce(lambda f_sum, next_item: f_sum + next_item[1],
                                self._frequencies_list[string], 0)

            self._frequencies_list[string] = [(s, 1.0 * v / normalizer)
                                          for s, v in self._frequencies_list[string]]

    def rescan_frequencies(self, text):
        self._frequencies_map = {}
        self.scan_frequencies(text)


    def next_symbol(self, string):
        rand_value = random()
        if string not in self._frequencies_list:
            return ' '

        cumm_sum = 0
        for symbol, weight in self._frequencies_list[string]:
            cumm_sum += weight
            if cumm_sum >= rand_value:
                return symbol

        return self._frequencies_list[string][-1]


    def generate(self, size):
        random_index = randint(0, len(self._frequencies_list) - 1)
        idx = 0
        for key in self._frequencies_list.keys():
            if idx == random_index:
                current_string = key
            idx += 1

        text = [current_string]

        for _ in range(size):
            text.append(self.next_symbol(current_string))
            current_string = current_string[1:] + text[-1]
        return "".join(text)

@click.command()
@click.option("-d", "--scan-depth", default=3, type=click.IntRange(1, 10), help="scanner depth")
@click.option("-l", "--length", type=int, required=True, help="result text length")
@click.argument("input_files", type=click.Path(exists=True, dir_okay=False), required=True, nargs=-1)
def cli(scan_depth, length, input_files):
    gen = MarkovGenerator(scan_depth)

    for path in input_files:
        with open(path) as file:
            gen.scan_frequencies(file.read())

    generated_text = gen.generate(length)
    print(generated_text)

if __name__ == "__main__":
    cli()
