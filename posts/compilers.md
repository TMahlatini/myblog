---
title: Compilers are cool
published: 2026-02-21
---

A month or two ago, I read a blog post titled [“The indifference engine”.](https://ponnekanti.net/indifference/) For brevity, I’ve extracted a paragraph that summarizes the core idea: 

*“...Perhaps the greatest faculty we developed in this gestation was not civilisation, but dispassion to its fruits: to be awed is human, to be indifferent divine. The more I think about this indifference the more remarkable it seems to me. The capacity to be apathetic to an iPhone is a far greater feat than to actually make the iPhone; it is a small miracle that people don’t instantly collapse into psychosis when they see one.”* 

Since first reading that, I have wanted to reflect more broadly on human ingenuity. However, I’ve decided to narrow my focus to software engineering—specifically, the ingenuity of compilers. My current project at work involves researching how artificial neural networks are compiled for various deployment strategies, and it is fascinating, to say the least.  

Occasionally, I try to explain what I do at work to my dad. Last week, I found it particularly difficult to explain my current project. Because my description wasn't satisfactory, I decided to write about it as simply as I can for his benefit—and perhaps, in the process, awaken your senses to the "indifference engine" already running inside you. With the rapid evolution of AI, it’s easy to forget that it is all ones and zeros underneath. The complexity of it all has been cleverly abstracted away and it's so good you can’t be bothered to ask how your phone can talk back to you. 

Let’s talk about compilers.(Disclaimer: I have oversimplified some of the concepts but the core principles remain)

**What is a compiler?**

In simple terms, it is a translator. It takes one language and converts it into another, much like Google Translate. The difference is that in computing, compilers translate between **high-level** (human-readable) and **low-level** (computer-friendly) languages. 
 
For accuracy, you can think of this as a multistage process—like translating English to French, then French to Spanish. Let’s look at a simple function that adds two numbers, where `a` and `b` are placeholders:


```
def  sum(a, b):
   return a + b

# example
sum(3,4) = 7 
```

However, a computer doesn't understand this text. It only understands 1s and 0s. So, first the compiler will translate that function into **Assembly language** (a human-readable version of what the machine actually does). Each line in Assembly language is an instruction the computer needs to execute and it looks something like this (I have added some comments for your benefit):

```
push   rbp          ; Prepare a space in memory for the task
mov    rbp, rsp     ; Set up the "base" of that space
mov    edi, eax     ; Move the first number (a) into a register (memory)
add    esi, eax     ; Add the second number (b) to it
pop    rbp          ; Clean up the memory space
ret                 ; Return the final result
```

We are now close, but not quite at 1s and 0s yet. An **Assembler** (another type of translator) then performs the final conversion into **Binary**. For example:

```
mov    edi, eax   -> 10001001 11111000
add    esi, eax   -> 00000001 11110000
ret               -> 11000011
```

Computers only understand these binary strings because they are made of billions of "on and off" switches called **transistors**. Depending on which switches are flipped, you get a different output.

Now, consider this: to get to where we are today, someone had to manually put together a sequence of 0s and 1s to build the very first assembler for the very first compiler. We are standing on top of a mountain of abstractions! 

Can you imagine how complex this process looks for Large Language Models like ChatGPT? Remember, it’s all 1s and 0s underneath. I will continue the technical discussion in a future post, but before I conclude, I want to leave you with this:

When we were children, we wondered about everything; the simplest things could fascinate us. At some point, the “indifference engine” kicked in. I suppose that is a necessary human adaptation—it allows us to move forward without being paralyzed by awe at every turn. But therein lies a danger. The more indifferent we are toward a system—whether it is politics, religion, or science—the more blinded we become to its fragility, or worse, its impact on us.

Technology is a double-edged sword, with one side significantly sharper than the other. We cannot afford to be too comfortable in our apathy; if we are, we may wake up one day to discover we have traded our humanity for convenience. Or, through our ingratitude toward the innovators and their complex systems, we might find we have burned them on the stake like witches. 
 
The irony in this reflection is the more I learn to appreciate the complexity upon which modern infrastructure is built, the more I want to live on some remote farm in the mountains, completely disconnected from it all. 
 
**A parting quote:**

*“Any sufficiently advanced technology is indistinguishable from magic.” — Arthur C. Clarke, Profiles of the Future*
