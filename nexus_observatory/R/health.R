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
  # Invoke the utility with structured arguments; do not ask a shell to parse a pipeline.
  output <- suppressWarnings(system2("df", c("-P", "/"), stdout = TRUE, stderr = FALSE))
  status <- attr(output, "status")
  if (!is.null(status) && status != 0L) return(NA)
  if (length(output) < 2L) return(NA)

  fields <- strsplit(trimws(output[[2L]]), "\\s+")[[1L]]
  if (length(fields) < 5L) return(NA)
  usage <- suppressWarnings(as.numeric(sub("%$", "", fields[[5L]])))
  if (!is.finite(usage)) return(NA)
  usage < threshold
}

.check_memory <- function(min_mb = 128) {
  if (!nzchar(Sys.which("free"))) return(NA)
  output <- suppressWarnings(system2("free", "-k", stdout = TRUE, stderr = FALSE))
  status <- attr(output, "status")
  if (!is.null(status) && status != 0L) return(NA)

  mem_line <- output[startsWith(trimws(output), "Mem:")]
  if (!length(mem_line)) return(NA)
  fields <- strsplit(trimws(mem_line[[1L]]), "\\s+")[[1L]]
  if (length(fields) < 7L) return(NA)
  available_kb <- suppressWarnings(as.numeric(fields[[7L]]))
  if (!is.finite(available_kb)) return(NA)
  (available_kb / 1024) >= min_mb
}
