# The Essence of Bayesian Reasoning: Monty Hall and the Art of Updating Beliefs

*A companion piece to "Understanding Bayesian Networks and Beyond"*

**Date:** January 20, 2026
**Audience:** Second-year undergraduates

---

## 1. The Puzzle That Stumped Mathematicians

In 1990, a reader wrote to Marilyn vos Savant's column in *Parade* magazine with this puzzle:

> Suppose you're on a game show, and you're given the choice of three doors. Behind one door is a car; behind the others, goats. You pick a door, say No. 1, and the host, who knows what's behind the doors, opens another door, say No. 3, which has a goat. He then says to you, "Do you want to switch to door No. 2?" Is it to your advantage to switch?

Marilyn answered: **Yes, you should switch. Switching gives you a 2/3 chance of winning; staying gives you only 1/3.**

Nearly 10,000 readers wrote in to say she was wrong—including nearly 1,000 with PhDs. They argued that after a door is opened, there are two doors left, so it's 50-50. Switching shouldn't matter.

They were all wrong. Marilyn was right. And understanding *why* she was right is understanding the essence of Bayesian reasoning.

---

## 2. The Essence of Bayesian Reasoning

Bayesian reasoning comes down to one fundamental insight:

> **When you learn something new, you should update your beliefs—but how much you update depends on what you believed before.**

This is captured in Bayes' theorem:

```
P(Hypothesis | Evidence) = P(Evidence | Hypothesis) × P(Hypothesis) / P(Evidence)
```

In plain English:

```
Your new belief = How likely the evidence would be if your hypothesis is true
                  × Your old belief
                  ÷ How likely the evidence is overall
```

The key terms:
- **P(Hypothesis)**: Your **prior**—what you believed before seeing evidence
- **P(Evidence | Hypothesis)**: The **likelihood**—how probable the evidence is if your hypothesis is true
- **P(Hypothesis | Evidence)**: Your **posterior**—what you should believe after seeing evidence

The magic of Bayesian reasoning is that it tells you *exactly* how to update. Not "a little" or "a lot"—a precise amount determined by the math.

---

## 3. The Monty Hall Problem, Step by Step

Let's apply Bayesian reasoning to the three-door puzzle.

### Setup

- Three doors: A, B, C
- One has a car, two have goats
- You pick door A
- Monty (who knows where the car is) opens door C, revealing a goat
- Should you switch to door B?

### Step 1: Establish Your Prior

Before Monty opens anything, what do you believe?

The car is equally likely to be behind any door:
- P(Car behind A) = 1/3
- P(Car behind B) = 1/3
- P(Car behind C) = 1/3

You picked door A. So your prior belief that you picked correctly is **1/3**.

### Step 2: Consider What Monty's Action Tells You

Here's where people go wrong. They think: "Monty opened door C. Now there are two doors. So it's 50-50."

But this ignores crucial information: **Monty's choice was not random.** Monty knows where the car is, and Monty *always* opens a door with a goat.

Let's think about what Monty *would have done* in each scenario:

**Scenario 1: Car is behind A (your door)**
- Monty can open either B or C (both have goats)
- He randomly picks one—let's say he opens C
- Probability Monty opens C in this scenario: **1/2**

**Scenario 2: Car is behind B**
- Monty can't open B (car is there)
- Monty can't open A (you picked it)
- Monty *must* open C
- Probability Monty opens C in this scenario: **1**

**Scenario 3: Car is behind C**
- Monty can't open C (car is there)
- But wait—Monty DID open C and there was a goat
- This scenario is impossible given what we observed
- Probability: **0**

### Step 3: Apply Bayes' Theorem

Now we can calculate. We want P(Car behind B | Monty opened C).

**Using Bayes:**

```
P(Car at B | Monty opens C) = P(Monty opens C | Car at B) × P(Car at B) / P(Monty opens C)
```

We need P(Monty opens C) overall. Using the law of total probability:

```
P(Monty opens C) = P(opens C | car at A) × P(car at A)
                 + P(opens C | car at B) × P(car at B)
                 + P(opens C | car at C) × P(car at C)

                 = (1/2 × 1/3) + (1 × 1/3) + (0 × 1/3)
                 = 1/6 + 1/3 + 0
                 = 1/2
```

Now:

```
P(Car at B | Monty opens C) = (1 × 1/3) / (1/2) = (1/3) / (1/2) = 2/3
```

And:

```
P(Car at A | Monty opens C) = (1/2 × 1/3) / (1/2) = (1/6) / (1/2) = 1/3
```

**Result: Switching gives you 2/3 probability of winning. Staying gives you 1/3.**

---

## 4. The Intuition Behind the Math

The math is airtight, but let's build intuition for *why* this is true.

### Intuition 1: Your Original Choice Was Probably Wrong

When you first picked door A, you had a 1/3 chance of being right and a 2/3 chance of being wrong.

Monty opening a door *doesn't change whether you were originally right or wrong*. The car didn't move. You either picked correctly or you didn't.

If you were wrong (2/3 chance), the car is behind one of the other doors. Monty just showed you which one it's NOT behind. So switching wins.

If you were right (1/3 chance), switching loses.

Switching wins when you were originally wrong. You were originally wrong 2/3 of the time. So switching wins 2/3 of the time.

### Intuition 2: Monty's Action Concentrates Probability

Before Monty acts:
- 1/3 probability is on door A
- 1/3 probability is on door B
- 1/3 probability is on door C

Monty opens door C, showing a goat. That 1/3 probability on door C has to go somewhere. But it doesn't split evenly between A and B!

Here's why: Monty *couldn't* have opened door C if the car was behind door C. And Monty *had to* open door C if the car was behind door B (since he couldn't open A or B).

The probability from door C gets **concentrated onto door B**, not split between A and B. Door B absorbs door C's probability because Monty's constrained choice linked them.

### Intuition 3: Imagine 100 Doors

This makes the intuition even clearer. Imagine 100 doors, one with a car, 99 with goats.

You pick door 1. Monty opens 98 doors, all showing goats, leaving only door 1 (yours) and door 57.

Now do you switch?

Of course! You originally had 1/100 chance. Monty just eliminated 98 wrong answers, *concentrating* the 99/100 probability that you were wrong onto the one door he didn't open.

Door 57 now has 99/100 probability. Your door still has 1/100.

The three-door case works the same way—it's just less dramatic (2/3 vs 1/3 instead of 99/100 vs 1/100).

---

## 5. Why People Get It Wrong

The Monty Hall problem reveals several cognitive biases:

### Bias 1: Ignoring the Prior

People see two doors and think "50-50." They're computing P(A) and P(B) as if they have no prior information.

But you DO have prior information: you picked door A when you had only 1/3 chance of being right. That prior doesn't disappear when Monty opens a door.

### Bias 2: Ignoring the Process

People treat Monty's door opening as random—as if someone accidentally opened a door. But Monty's action was *constrained*: he knew where the car was and deliberately avoided it.

Bayesian reasoning requires you to model the *process* that generated the evidence, not just the evidence itself.

### Bias 3: The Illusion of New Choice

When Monty asks "Do you want to switch?", it feels like a fresh decision between two equal options. But it's not—it's a continuation of your original choice, with new information.

Your choice to stay is really a choice to bet on your original 1/3 guess. Your choice to switch is to bet on the remaining 2/3.

---

## 6. Connection to Bayesian Networks

The Monty Hall problem is a tiny Bayesian network:

```
    Car Location
     /        \
    ↓          ↓
Your Pick    Monty's Choice
    \          /
     ↓        ↓
     Your Decision
```

- **Car Location**: Hidden variable (A, B, or C)
- **Your Pick**: Observed (you chose A)
- **Monty's Choice**: Observed (he opened C)
- **Question**: Given Your Pick = A and Monty's Choice = C, what is P(Car Location = B)?

This is exactly the kind of query that Bayesian networks are designed to answer. The key insight is that **Monty's Choice is not independent of Car Location**—there's a causal arrow from Car Location to Monty's Choice (Monty's behavior depends on where the car is).

Pearl's graphical notation makes this explicit. In a network diagram, you can *see* that Monty's choice depends on the car location, which prevents the naive "50-50" error.

---

## 7. Connection to Our Quinean System

The Monty Hall problem also illustrates something important about our coherentist system.

### Bayesian Updating vs. Coherence Adjustment

In classic Bayesian reasoning (and in Monty Hall), you have:
- A fixed hypothesis space (car behind A, B, or C)
- A well-defined likelihood function (P(Monty opens C | car at X))
- A clean update rule (Bayes' theorem)

But scientific knowledge is messier. When a new study comes in:
- The hypothesis space might need revision (maybe there's a theory we haven't considered)
- The likelihood isn't known precisely (how probable is this result if ART is true?)
- Multiple beliefs adjust simultaneously, not just one

Our Quinean system handles this messiness through **coherence adjustment** rather than **Bayesian updating**:

| Aspect | Bayesian Updating | Coherence Adjustment |
|--------|------------------|---------------------|
| Hypothesis space | Fixed | Can grow (new theories, stubs) |
| Likelihoods | Known precisely | Estimated, uncertain |
| Update | Single belief | Whole web adjusts |
| Foundation | Observations bedrock | Everything revisable |

### What We Keep

But we keep the *essence* of Bayesian reasoning:

1. **Priors matter**: What you believed before affects what you should believe now
2. **Evidence quality matters**: Strong evidence updates more than weak evidence
3. **The process matters**: How evidence was generated affects its meaning
4. **Update, don't replace**: New information adjusts beliefs; it doesn't erase prior knowledge

In our system, when a new study arrives:
- Its impact depends on what we believed before (priors)
- High-quality studies shift credences more (evidence quality)
- We consider how the study was conducted (the process)
- We adjust existing beliefs, not start from scratch (update)

---

## 8. The Deep Lesson

The Monty Hall problem teaches a profound lesson: **your beliefs should be responsive to evidence, but the right response depends on the structure of the situation**.

The naive response ("two doors, so 50-50") ignores the structure. The Bayesian response accounts for:
- Your prior beliefs (1/3 for each door)
- The process generating evidence (Monty's constrained choice)
- How these combine (Bayes' theorem)

This is why explicit structure matters. In a Bayesian network, the structure (the arrows) tells you what depends on what. In our Quinean web, the constraints tell you how beliefs relate.

Without structure, you're guessing. With structure, you're reasoning.

---

## 9. Summary

**The essence of Bayesian reasoning:**
1. Start with prior beliefs
2. Observe evidence
3. Update beliefs based on how likely the evidence would be under different hypotheses
4. The posterior combines prior belief with evidence—it's not determined by evidence alone

**Monty Hall teaches us:**
- Prior probabilities persist through new information
- The *process* generating evidence matters (Monty's choice was constrained)
- Probability can concentrate (door C's probability flows to door B)
- Intuition fails; math saves us

**Connection to our systems:**
- Bayesian Networks make structure explicit, preventing errors
- Our Quinean system extends this to handle scientific messiness
- Both respect the core insight: beliefs should update based on evidence *and* structure

**The bottom line:**

When Monty opens door C, he's not giving you a fresh 50-50 choice. He's giving you information that concentrates the probability of being wrong (which was 2/3) onto a single door. Switching is just betting that you were probably wrong initially—which you were.

Always switch.

---

## Appendix: The Math in Full

For completeness, here's the full Bayesian calculation.

**Notation:**
- C_A = "Car is behind door A"
- C_B = "Car is behind door B"
- C_C = "Car is behind door C"
- M_C = "Monty opens door C"

**Given:**
- You picked door A
- Monty opened door C, showing a goat

**Priors:**
- P(C_A) = P(C_B) = P(C_C) = 1/3

**Likelihoods (given you picked A):**
- P(M_C | C_A) = 1/2  (Monty chooses randomly between B and C)
- P(M_C | C_B) = 1    (Monty must open C; can't open A or B)
- P(M_C | C_C) = 0    (Monty can't open C if car is there)

**Total probability of M_C:**
```
P(M_C) = P(M_C|C_A)P(C_A) + P(M_C|C_B)P(C_B) + P(M_C|C_C)P(C_C)
       = (1/2)(1/3) + (1)(1/3) + (0)(1/3)
       = 1/6 + 2/6 + 0
       = 3/6 = 1/2
```

**Posteriors:**
```
P(C_A | M_C) = P(M_C|C_A) × P(C_A) / P(M_C)
             = (1/2 × 1/3) / (1/2)
             = (1/6) / (1/2)
             = 1/3

P(C_B | M_C) = P(M_C|C_B) × P(C_B) / P(M_C)
             = (1 × 1/3) / (1/2)
             = (1/3) / (1/2)
             = 2/3

P(C_C | M_C) = P(M_C|C_C) × P(C_C) / P(M_C)
             = (0 × 1/3) / (1/2)
             = 0
```

**Verification:** 1/3 + 2/3 + 0 = 1 ✓

**Conclusion:** P(win by switching) = P(C_B | M_C) = **2/3**

---

*Essay prepared for COGS 101 students, January 2026*
