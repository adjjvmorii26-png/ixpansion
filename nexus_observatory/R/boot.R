#' Boot the Nexus Observatory system
#'
#' Invokes the shell-based boot script, loading all modules from
#' \code{modules.d/} in numbered order.
#'
#' @param verbose Print debug output.
#' @param dry_run Preview actions without executing.
#' @return Invisibly returns the exit code of the boot process.
#' @export
nexus_boot <- function(verbose = FALSE, dry_run = FALSE) {
  args <- c("boot")
  if (verbose) args <- c(args, "-v")
  if (dry_run) args <- c(args, "--dry-run")

  script <- system.file("nexus_boot.sh", package = "nexusObservatory")
  if (!nzchar(script)) {
    stop("nexus_boot.sh not found in installed package.")
  }
  status <- suppressWarnings(system2(script, args, stdout = "", stderr = ""))
  invisible(status)
}

#' Show current Nexus Observatory status
#'
#' @return Invisibly returns the exit code.
#' @export
nexus_status <- function() {
  script <- system.file("nexus_boot.sh", package = "nexusObservatory")
  status <- suppressWarnings(system2(script, "status", stdout = "", stderr = ""))
  invisible(status)
}
