# How we're building this




## Round one

> "Build one to throw one away."

So we got the version 1.0 working, and after many many hours it can crank out something like this:

<p float= "left">
<img src="./data/RamiSquare.png" width="30%" />
<img src="./data/Run_000004270.png" width="30%" />
</p>


To be honest, it cranks out something like this in about an hour, and then it
stablizes to what seems to be the local maximum: a pink-ish square in front of a dark green square.

So it works, which is good, but we would like it to do better. There are various things we could tune, like:
- The scoring function between the reference image and the one under iteration.
- The various hyperparameters in the evolution like amount of kids and mutation rate. 
- The more generic config of the run like amount of boxes.

These are a fine target for hyperparameter tuning, but the problem is that this thing is really slow at the moment. A single step in the evolution takes more than a second, and it seems that we need hundreds of steps to evolve. So we need to make it faster. (At the same time, we'll probably want to make it a bit cleaner as well. This has been the "throw one away" -version.)

### Speedup plans

As we learned in [speeding up sudokus](https://github.com/ramiluisto/SudokuSpeedTests) we should first try to actually see where the time goes in the iterations. We should also hope that maybe this time with arrays of size `512x512x3` using Numpy might actually provide a boost.


So let's run the system for 5 steps under the profiler to see where the CPU time is going on this one:
```bash
python -m cProfile -o first_version_5_rounds.prof longrun.py
```

After this command we'll look at the data with the classical:
```
$ python -m pstats first_version_5_rounds.prof 
Welcome to the profile statistics browser.
first_version_5_rounds.prof% strip
first_version_5_rounds.prof% sort cumtime
first_version_5_rounds.prof% stats 10
[...]
first_version_5_rounds.prof% sort tottime
first_version_5_rounds.prof% stats 10
```

Cumulative times:
```bash
Tue Mar 21 06:47:01 2023    first_version_5_rounds.prof

         147529006 function calls (147522255 primitive calls) in 233.793 seconds

   Ordered by: cumulative time
   List reduced from 985 to 10 due to restriction <10>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     97/1    0.001    0.000  233.793  233.793 {built-in method builtins.exec}
        1    0.000    0.000  233.793  233.793 longrun.py:1(<module>)
      112    0.793    0.007  232.166    2.073 base_elements.py:90(score)
      112   13.001    0.116  230.036    2.054 base_elements.py:100(image_distance)
 29360240   58.428    0.000  211.379    0.000 base_elements.py:102(<genexpr>)
        6    0.000    0.000  198.172   33.029 evolution.py:25(do_one_round)
        6    0.057    0.010  197.277   32.879 evolution.py:30(<dictcomp>)
 29360128  131.289    0.000  152.951    0.000 base_elements.py:109(point_distance)
        1    0.000    0.000   35.141   35.141 evolution.py:10(__init__)
        1    0.017    0.017   35.119   35.119 evolution.py:12(<dictcomp>)
```

Total times:

```bash
         147529006 function calls (147522255 primitive calls) in 233.793 seconds

   Ordered by: internal time
   List reduced from 985 to 10 due to restriction <10>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
 29360128  131.289    0.000  152.951    0.000 base_elements.py:109(point_distance)
 29360240   58.428    0.000  211.379    0.000 base_elements.py:102(<genexpr>)
 88080480   21.662    0.000   21.662    0.000 {built-in method builtins.abs}
      112   13.001    0.116  230.036    2.054 base_elements.py:100(image_distance)
     4144    4.803    0.001    4.803    0.001 {method 'decode' of 'ImagingDecoder' objects}
     1792    0.805    0.000    0.805    0.000 {method 'draw_polygon' of 'ImagingDraw' objects}
      112    0.793    0.007  232.166    2.073 base_elements.py:90(score)
      113    0.490    0.004    0.490    0.004 {built-in method builtins.sum}
    40448    0.262    0.000    0.430    0.000 base_elements.py:170(number_to_code_string)
      112    0.222    0.002    0.222    0.002 {built-in method PIL._imaging.fill}
```

So it seems we are spending **a lot** of time on lines 90, 100, 102 and 109. Below is (slightly reordered, lines don't actually count up right) the area in questions:
```python
    def score(self, comparison_image=None): # LINE 90
        if comparison_image == None:
            comparison_image = Image.open(DEFAULT_TEST_IMAGE_FILEPATH)
        current_image = self.draw()
        score = self.image_distance(current_image, comparison_image)
        return score

    def image_distance(self, current_image, comparison_image): # LINE 100
        distances = tuple(
            self.point_distance(curr, comp) # THE <genexpr> OF LINE 102
            for curr, comp in zip(current_image.getdata(), comparison_image.getdata())
        )
        return sum(distances) / len(distances)

    def point_distance(self, rgb_1, rgb_2): # LINE 109
        distance = 0
        for a, b in zip(rgb_1, rgb_2):
            distance += abs(b - a) / 256.0 # ONLY PLACE WHERE abs() is used.
        return distance / 3.0
``` 