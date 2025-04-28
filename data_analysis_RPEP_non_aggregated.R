
#0. data loading and making a subset which discards the one participant with low accuracy
Data.long.full <- read.csv("/Users/miralombaert/Desktop/RPEP/RPEPprocessed_datafiles/final_dataframe/RPEP_dataframe_non_aggregated.csv")
Data.long.subset <- subset(Data.long.full, subject != 49) # Remove participant with number 5 due to its extremely low accuracy

head(Data.long.full)
dim(Data.long.full)
dim(Data.long.subset) #some rows are missing because participant 18 has missing data!


#1. setting all factors and checking the levels of the factors

    # Let R know which predictors are factors
Data.long.full$interval <-factor (Data.long.full$interval)
Data.long.subset$interval <-factor (Data.long.subset$interval)
levels(Data.long.subset$interval)

Data.long.full$distractor_size <-factor (Data.long.full$distractor_size) 
Data.long.subset$distractor_size <-factor (Data.long.subset$distractor_size) 
levels(Data.long.subset$distractor_size)

Data.long.full$correctresponse_location <-factor (Data.long.full$correctresponse_location) 
Data.long.subset$correctresponse_location <-factor (Data.long.subset$correctresponse_location) 
levels(Data.long.subset$correctresponse_location)

Data.long.full$product <-factor (Data.long.full$product) 
Data.long.subset$product <-factor (Data.long.subset$product) 
levels(Data.long.subset$product)

Data.long.full$Block <-factor (Data.long.full$Block)
Data.long.subset$Block <-factor (Data.long.subset$Block)
levels(Data.long.subset$Block)

Data.long.full$Gender <-factor (Data.long.full$Gender)
Data.long.subset$Gender <-factor (Data.long.subset$Gender)
levels(Data.long.subset$Gender)

Data.long.full$Handedness <-factor (Data.long.full$Handedness)
Data.long.subset$Handedness <-factor (Data.long.subset$Handedness)
levels(Data.long.subset$Handedness)

Data.long.full$subject <-factor (Data.long.full$subject)
Data.long.subset$subject <-factor (Data.long.subset$subject)
levels(Data.long.subset$subject)


#2. visualizing the data
library(lattice)

  #2.1 boxplot of the accuracy rate to justify excluding one participant

    #with outlier included
boxplot(Data.long.full$accuracy_rate, 
        main = "Boxplot of Accuracy Rate", 
        ylab = "Accuracy Rate", 
        col = "lightblue") 
    #when outlier is removed
boxplot(Data.long.subset$accuracy_rate, 
        main = "Boxplot of Accuracy Rate", 
        ylab = "Accuracy Rate", 
        col = "lightblue") 

  #2.2 cognitive depletion? NO!
print(bwplot (RT ~ Block, data= Data.long.subset, main = "Boxplot of RT per block") ) 

  #2.3 handedness, gender
print(bwplot (RT ~ Gender, data= Data.long.subset, main = "Boxplot of RT per gender") ) 
print(bwplot (RT ~ Handedness, data= Data.long.subset, main = "Boxplot of RT per handedness") )

  #2.4 visualizing the RT over intervals, separate for left vs right response
print(xyplot (RT ~ interval, groups = correctresponse_location, data = Data.long.subset, main = "RT ~ interval:response", type= c("a", "g"), auto.key = list(space = "right", points = FALSE, lines = TRUE)))

  #2.5 justifying the random effects that we predict to be necessary

    #2.5.1 visualize the need for intercept-by subject
library(ggplot2)

ggplot(Data.long.subset, aes(x = subject, y = RT)) +
  geom_boxplot() +
  labs(title = "Boxplot of RT per Participant", x = "Participant", y = "RT") +
  theme(axis.text.x = element_text(angle = 90, hjust = 1, size = 8))  # Rotate & resize labels

    #2.5.2 visualize the need for intercept-by product
library(ggplot2)

ggplot(Data.long.subset, aes(x = product, y = RT)) +
  geom_boxplot() +
  facet_wrap(~ interval, scales = "free_x") +  # Facet by interval
  labs(title = "Boxplot of RT by Product and Interval", x = "Product", y = "RT") +
  theme(axis.text.x = element_text(angle = 90, hjust = 1, size = 8))  # Rotate & resize x-axis labels

    #2.5.3 correctresponse location slope by subject
print(xyplot (RT ~ interval|subject, groups = correctresponse_location, data = Data.long.subset, type= c("a", "g"), auto.key = list(space = "right", points = FALSE, lines = TRUE)))

#3. descriptive statistics
library(reshape2)
Data.long.subset.melt <- melt(Data.long.subset, measure.vars= "RT") 
head(Data.long.subset.melt)

  #how many subjects? gender, age, handedness
table(unique(Data.long.subset.melt[, c("subject", "Gender", "Age", "Handedness")])[, c("Age")])
table(unique(Data.long.subset.melt[, c("subject", "Gender", "Age", "Handedness")])[, c("Gender")])
table(unique(Data.long.subset.melt[, c("subject", "Gender", "Age", "Handedness")])[, c("Handedness")])

  #mean and sd for age, median and IQR for accuracy rate and value
mean(Data.long.subset.melt$Age)
sd(Data.long.subset.melt$Age)
median(Data.long.subset.melt$accuracy_rate)
IQR(Data.long.subset.melt$accuracy_rate)
median(Data.long.subset.melt$value)
IQR(Data.long.subset.melt$value)

  #table of the median and IQR for RT per correctresponselocation:interval, for RT per correctresponse location
median_perinterval_table <- dcast(correctresponse_location ~ interval, data = Data.long.subset.melt, median)
IQR_perinterval_table <- dcast(correctresponse_location ~ interval, data = Data.long.subset.melt, IQR)
median_perlocation_table <- dcast(correctresponse_location ~., data = Data.long.subset.melt, median)
IQR_perlocation_table <- dcast(correctresponse_location ~., data = Data.long.subset.melt, IQR)

  #observations per product or per solution or per interval: 
table(Data.long.subset$product, Data.long.subset$correctresponse_location) #per product
table(Data.long.subset$solution, Data.long.subset$correctresponse_location) #per solution
table(Data.long.subset$interval, Data.long.subset$correctresponse_location) #per interval


#4. linear mixed model modern univariate approach

library(Matrix)
library(lme4)

    #first standardize/center the solution variable, important !
Data.long.subset$solution_z <- scale(Data.long.subset$solution) #solution_z = the standardized version of solution

    #second, set the contrasts to effect coding, allowing type 3 testing if wanted to
options(contrasts = c("contr.sum", "contr.poly")) #effect coding
contrasts(Data.long.subset$correctresponse_location) 

  #4.1 model building: which random effects should be included? 

        #first comparison
fit0 <- lmer(RT ~ 1 + (1| subject),data = Data.long.subset) 
fit1 <- lmer(RT ~ 1 + (1| subject) + (1|product),data = Data.long.subset) 
anova(fit0, fit1) #fit 1 is better

        #second comparison
fit2 <- lmer(RT ~ 1 + solution_z + correctresponse_location + 
               solution_z:correctresponse_location + (1| subject) + (1|product),
             data = Data.long.subset) 
fit3 <- lmer(RT ~ 1 + solution_z + correctresponse_location + 
                    solution_z:correctresponse_location + (1 + solution_z| subject) + (1|product),
                  data = Data.long.subset) 
anova(fit2, fit3) #fit 3 is better, but the difference is not highly significant

fit4 <- lmer(RT ~ 1 + solution_z + correctresponse_location + 
               solution_z:correctresponse_location + (1 + correctresponse_location| subject) 
             + (1|product),data = Data.long.subset) #fit 4 is better, the difference is highly significant ! This is the final model

anova(fit2, fit4)

fit5 <- lmer(RT ~ 1 + solution_z + correctresponse_location + solution_z:correctresponse_location + 
               (1 + correctresponse_location + solution_z:correctresponse_location| subject) 
             + (1|product),data = Data.long.subset) #singularity issues! 

  #4.2 are all assumptions met? 
  
    #4.2.1 everything apart
      #linearity of fixed effects: should be a straight line
plot(fitted(fit4), resid(fit4), 
     xlab = "Fitted Values", ylab = "Residuals", 
     main = "Residuals vs Fitted")
abline(h = 0, col = "red")

      #normality of random effects: seems ok!
ranef_vals <- ranef(fit4)$subject[,1]
qqnorm(ranef_vals, main = "Q-Q Plot of Random Effects")
qqline(ranef_vals, col = "red")

      #normality of residuals: not completely ok
hist(resid(fit4), breaks = 30, main = "Histogram of Residuals", col = "lightblue")
qqnorm(resid(fit4))
qqline(resid(fit4), col = "red")


      #homoscedasticity
ggplot(data.frame(fitted = fitted(fit4), resid = resid(fit4)), aes(x = fitted, y = resid)) +
  geom_point(alpha = 0.5) +
  geom_smooth(method = "loess", col = "red") +
  labs(title = "Homoscedasticity Check", x = "Fitted Values", y = "Residuals")

ggplot(data.frame(num_mag = Data.long.subset$solution_z, resid = resid(fit4)), aes(x = num_mag, y = resid)) +
  geom_point(alpha = 0.5) +
  geom_smooth(method = "loess", color = "red") +
  labs(title = "Residuals vs. Number Magnitude", x = "Number Magnitude", y = "Residuals")

#this plot shows how residuals are distributed for different magnitudes
plot(Data.long.subset$solution_z, resid(fit4), 
     xlab = "Product Magnitude", 
     ylab = "Residuals", 
     main = "Residuals vs. Product Magnitude")
abline(h = 0, col = "red")

      #multicolinearity
library(car)
vif(lm(RT ~ solution * correctresponse_location, data = Data.long.subset))



  #4.3 model output

# uses satterwaite's method for estimation of degrees of freedom, 
# as there are no factors with more than 2 levels, 
# no huge need for concern for sphericity!

library(lmerTest)
fit4 <- lmer(RT ~ 1 + solution_z + correctresponse_location + 
               solution_z:correctresponse_location + 
               (1 + correctresponse_location | subject) + 
               (1 | product),
             data = Data.long.subset)
summary(fit4) #summary now includes satterwaites degrees of freedom and p-values
confint(fit4, method = "Wald") #confidence intervals for the fixed effects


  #4.4 visualizing the effects

dev.off()  # Close the current graphics device
library(effects)
library(ggplot2)

  # Get effect data
effect_data <- as.data.frame(allEffects(fit4))

  # Plot using ggplot2
ggplot(effect_data[[1]], aes(x = solution_z, y = fit, color = correctresponse_location, group = correctresponse_location)) +
  geom_line(size = 1) +  # Interaction line
  geom_point(size = 2) +  # Points for estimates
  geom_errorbar(aes(ymin = lower, ymax = upper), width = 0.1) +  # Confidence intervals
  labs(
       x = "Product Magnitude", 
       y = "Predicted RT",
       color = "Response Location") +
  theme_minimal() +
  theme(text = element_text(size = 14))

library(sjPlot)
plot_model(fit4, type = "int")



#5 Effect size: Cohen's f2

library(lme4)
library(performance)


    #5.2.1 extract all data needed for the calculation: 

fit4full <- lmer(RT ~ 1 + solution_z + correctresponse_location + 
               solution_z:correctresponse_location + (1 + correctresponse_location| subject) 
             + (1|product),data = Data.long.subset) 

fit4red <- lmer(RT ~ 1 + solution_z + correctresponse_location + 
                        (1 + correctresponse_location| subject) 
                        + (1|product),data = Data.long.subset) 

r2(fit4full)
r2(fit4red)
Rfull <- 0.016
Rred <- 0.015
f <- (Rfull - Rred) / (1-Rfull)
