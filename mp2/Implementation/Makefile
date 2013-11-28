all: libmalloc.so test1 test2 test3
.PHONY: all

test%: test%.c
	gcc -g -Wall -Werror $< -o $@

obj/:
	mkdir -p obj

obj/%.o: %.c %.h obj/
	gcc -g -fPIC -Wall -Werror -c $< -o $@

libmalloc.so: obj/malloc.o obj/memreq.o
	gcc -g -shared -Wl,-soname,$@ -o $@ obj/memreq.o obj/malloc.o

clean:
	rm -f obj/*.o test1 test2 test3 libmalloc.so
.PHONY: clean
