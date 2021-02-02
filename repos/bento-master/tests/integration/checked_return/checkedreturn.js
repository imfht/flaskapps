function must_be_used() {
  return true;
}

function must_not_be_used() {
  return true;
}

function test_must_be_used() {
  var x;
  var list = [];
  if ((x = must_be_used())) {
  }
  x = must_be_used();
  x = must_be_used();
  x = must_be_used();
  x = must_be_used();

  x = must_be_used();
  x = must_be_used();
  x = must_be_used();
  x = must_be_used();
  x = must_be_used();

  //BUG:
  must_be_used();
  //maybe a bug, but not counted for now, maybe used for its throwing effect
  try {
    must_be_used();
  } catch (e) {}

  //Not a bug!
  x = list.map(() => must_be_used());
}

function test_ignore_local_var(must_be_used) {
  // Not a bug!
  must_be_used();
}