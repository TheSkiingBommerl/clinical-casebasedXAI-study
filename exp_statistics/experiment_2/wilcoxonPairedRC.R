# Matched-pairs rank biserial correlation coefficient

library(dplyr)
library(tidyr)
library(rcompanion)

records <- read.csv("exp_statistics/experiment_2/records_per_arm.csv")

wide <- records %>%
  pivot_wider(
    id_cols = c(participant, experience_level),
    names_from = arm,
    values_from = jaccard
  )

print(colnames(wide))
print(wide)

arms <- c("0", "1", "2", "3")
pairs <- combn(arms, 2, simplify = FALSE)


results <- lapply(pairs, function(p) {
  x_vals <- as.numeric(wide[[p[1]]])
  y_vals <- as.numeric(wide[[p[2]]])

  stacked_x <- c(x_vals, y_vals)
  stacked_g <- factor(rep(c(p[1], p[2]), each = length(x_vals)))
  
  rc_wilcoxon <- wilcoxonPairedRC(
    x = stacked_x, g = stacked_g,
    zero.method = "Wilcoxon", ci = TRUE, digits = 4
  )

  data.frame(
    pair = paste(p[1], "vs", p[2]),
    rc_wilcoxon = as.numeric(rc_wilcoxon["rc"]),
    ci_lower = as.numeric(rc_wilcoxon["lower.ci"]),
    ci_upper = as.numeric(rc_wilcoxon["upper.ci"])
    
  )
})

out <- do.call(rbind, results)

print(out)