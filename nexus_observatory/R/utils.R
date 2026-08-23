.list_modules <- function() {
  modules_dir <- system.file("modules.d", package = "nexusObservatory")
  if (!dir.exists(modules_dir)) return(character(0))
  sort(list.files(modules_dir, pattern = "\\.sh$", full.names = TRUE))
}
