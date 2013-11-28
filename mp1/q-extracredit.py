# Build a Sieve of Eratosthenes. Such a sieve is used to determine prime
# numbers, with filters in place to eliminate multiples of primes.
#
# You will need a producer thread which simply produces numbers 2 through 1000.
# These are all candidates for prime numbers.
#
# You will need a channel, through which numbers are communicated. This channel
# is analogous to the bounded buffer used in the producer consumer problem,
# except it can hold as few as one item at a time.
#
# You will need a consumer thread, with a given channel as an input. Any number
# that makes its way to the consumer is considered a prime number. Whenever a
# prime reaches the consumer, the consumer should print it, create a filter
# thread around this prime number and with the current channel as the new
# filter's input, and the filter's output as the consumer's new input.
#
# You will need filter threads, forked off by the consumer thread with a
# particular prime. These threads should read numbers from their input
# channels, check if the number is divisible by the prime with which they have
# been tasked from eliminating from the stream, and if the number is not evenly
# divisible by their prime, simply pass it on to their output.

# Use either monitors and condition variables, or semaphores.
