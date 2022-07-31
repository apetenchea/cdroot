let rec sum_helper acc n =
  if n = 1 then acc + 1
  else sum_helper (acc + n) (n - 1);;

let sum = sum_helper 0;;

let n = read_int() in
print_int (sum n);
print_newline();;