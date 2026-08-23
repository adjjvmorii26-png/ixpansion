#' Run full diagnostics on the host environment
#'
#' Checks dependencies, permissions, module availability,
#' disk space, memory, and network reachability.
#'
#' @return Invisibly returns the exit code of the doctor command.
#' @export
nexus_doctor <- function() {
  script <- system.file("nexus_boot.sh", package = "nexusObservatory")
  status <- suppressWarnings(system2(script, "doctor", stdout = "", stderr = ""))
  invisible(status)
}

#' Run individual health checks programmatically
#'
#' @return A named list of check results.
#' @export
nexus_health_check <- function() {
  list(
    disk_ok = .check_disk(),
    memory_ok = .check_memory(),
    bash_ok = nzchar(Sys.which("bash"))
  )
}

.check_disk <- function(threshold = 90) {
  usage <- as.numeric(
    gsub("%", "", system("df / | awk 'NR==2 {print $5}'", intern = TRUE))
  )
  usage < threshold
}

.check_memory <- function(min_mb = 128) {
  if (!nzchar(Sys.which("free"))) return(NA)
  avail_kb <- as.numeric(
    system("free | awk '/^Mem:/ {print $7}'", intern = TRUE)
  )
  (avail_kb / 1024) >= min_mb
}
