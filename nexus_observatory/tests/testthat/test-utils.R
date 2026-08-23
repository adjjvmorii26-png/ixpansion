test_that(".list_modules returns sorted module paths", {
  mods <- .list_modules()
  expect_true(all(grepl("\\.sh$", mods)))
  expect_identical(mods, sort(mods))
})

test_that("package version is valid semver", {
  desc <- read.dcf(system.file("DESCRIPTION", package = "nexusObservatory"))
  expect_match(desc[, "Version"], "^\\d+\\.\\d+\\.\\d+$")
})
