---
title: handy git recipes
date: 2023-05-01 19:28:52
tags:
- Programming
---

[Git](https://git-scm.com/) is one of these things I use on a daily basis, yet I've never felt like I truly mastered it.
There's so many things you can do with it, and so many ways to do them, that it's easy to get lost in the sea of commands and options.
Truth be told, just a couple of them are enough to leverage 90% of the power of git repositories and cover the main
needs of developers. That remaining 10% can be quite useful during complex workflows.  
I've put together explanations of the most commonly used terminology and commands, as well as some recipes which
I often find myself using at work. I hope you'll find them useful too. For the record, at the time of this writing
I was using git version 2.37.0.

## Basics

### Commits and Branches

**A commit is a snapshot of all the tracked files in your project.** It contains the changes made since the previous commit,
along with metadata such as the commit author, timestamp, and a message describing the changes. Commits are organized sequentially,
each commit pointing to its parent commit. This is how git records the history of a repository. Think about it
in terms of inheritance, instead of time: a commit inherits the changes of its parent commit, and adds its own changes
on top of them. Everything in git is relative to something prior. More formally, commits are organized as a
[directed acyclic graph](https://en.wikipedia.org/wiki/Directed_acyclic_graph). This way, it is easy to traverse the history
of a repository and do all kinds of useful operations on it.

![Git commits](https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/handy-git-recipes/media/commits.png)

Every commit is identified by a unique hash, which is a 40-character hexadecimal string. When working with commits, it's rarely necessary to
reference them by their full identifier. You can pass in only a prefix (first 7 characters should be enough), as
git is smart enough to figure out the rest, as long as there exists only one commit with the given prefix. For example, let's consider
commit [dc2727cdfe357e4caf40f9c79c35d5232195ca45](https://github.com/apetenchea/cdroot/commit/dc2727cdfe357e4caf40f9c79c35d5232195ca45)
from this blog's [repository](https://github.com/apetenchea/cdroot). You can check the metadata associated with it
by running `git --no-replace-objects cat-file commit dc2727c`. The output is:

```
tree 2f3a693e39a75ae5e393c226c17895e6136d2d72
parent b200f511526c750833abf07dd5749aad7be1132b
author Alex Petenchea <alex.petenchea@gmail.com> 1682878857 +0300
committer Alex Petenchea <alex.petenchea@gmail.com> 1682878857 +0300
gpgsig -----BEGIN PGP SIGNATURE-----

 iQIzBAABCAAdFiEE9yeY4Rbw/gqLPsLv9wg11DTo7E8FAmROsYkACgkQ9wg11DTo
 7E83CBAAxqwUzVdxOlMKxV5rsEs0Mx1/mh4O3dY4onjC7FZ5R/WFmNiMEGN9gDMP
 u9V72rj0kIvr4i+TERciueR5hgEZBcpo8fO2knZPXJMe3JrOZx1cF5Fe5dGQLgi2
 cIC8MwH3GUacRqpezFrFJWVbKtTY/mQ6a5UVOjZyg9kqJwE/otp7FgaR2Y0rC1kP
 hGU0N4lkWnlkaUxc9K4tNYfZgahKTQGug961T5wSxFLh6qlRj27shZQ7N9JKUCIn
 L+70hTJaLruisnqqgBse93OcCgFLOWuBkR5oxRe5vx5ZiLkXVZT9xusVpLpRxFEz
 CvlBTQpgJ9wlWujFJdw76015UMctEjnO+M3oGC5vAfYTmYxgyDQ9suWQDdbuULpV
 /ndA9LvZ72+BBgpIhTGOSSHcyg/Rd3A/trGgmZVkn4GAGCZJGzADKePANcPgs+iD
 AjdehqPwwwH/82Il2shojNMJ4mPt80gWE2W0DZypvneIrbZvQ59gDnXkjhF20tCr
 /xTRnfDVTq0pPfoeQ5Ks9f4Box+nIDdiB5FRdaddx1JDSiIWOu7dWCnfMCQDl2Ml
 aZgD6P+8SADCo/9NWqn/vSenzxFHtmXILrTasj58ed0hOVIPNvcCBRS2d/tbs/lx
 ozn2PNOUQvYUTfjt7SfR2Rjl3EvUFdrADdcDRb0G+Ox7yd0/JL4=
 =Q1hH
 -----END PGP SIGNATURE-----

Minor fixes
```

That is:
- The source tree: SHA-1 hash of the tree object representing the repository's file structure at the time of the commit.
- Commit parent(s): The SHA-1 hash(es) of the commit parent(s). A commit can have multiple parents in the case of a merge commit.
- Author: the name and email address of the person who authored the changes, along with the commit timestamp.
- Committer: the name and email address of the person who made the commit, along with the commit timestamp. This might be 
  different from the author if the changes were committed by another person.
- GPG signature: this is optional, and can be used to verify the authenticity of the commit. It is generated using the author's
  private key, and can be verified using their public key.
- Commit message: the text of the commit message.

All that information is combined and hashed using the SHA-1 algorithm to produce an unique commit identifier. Here's
how you can generate it yourself:
```bash
(printf "commit %s\0" $(git --no-replace-objects cat-file commit dc2727c | wc -c); git cat-file commit dc2727c) | sha1sum
```

For an explanation of the command above, check out [Carl Mäsak's gist](https://gist.github.com/masak/2415865). And finally,
to inspect the changes introduced with this commit, you can run `git show dc2727c`.  
The usual workflow is to add changes to the staging area, and then commit them.
```bash
git add . # stage all changes
git commit -m "explaining git"
```
The above was used to generate commit [a561329](https://github.com/apetenchea/cdroot/commit/a56132941d13867937334abc3de47765b49a36c8).
You may also use the shorthand `git commit -am "explaining git"`, which will automatically stage all changes before committing them.
However, note that this command will add and commit all the modified files, but not the *newly created* ones. Eventually,
you'll want to run `git push` to push your changes to the remote repository.

**Moving on to branches, a branch is just a pointer to a commit.** When you create a new branch, it points to the same commit as the branch
you created it from. When you commit changes to a branch, the branch pointer is updated to point to the new commit. 
The default branch of a repository is usually called `master` or `main`.

![Git commits](https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/handy-git-recipes/media/branching.gif)

Creating a new branch is done by running `git branch <branch-name>`. To switch to a branch, run `git checkout <branch-name>`.
These two are usually done together, so there's a shorthand for it: `git checkout -b <branch-name>`. Alternatively, you can
use `git switch <branch-name>` to switch to an existing branch, or `git switch -c <branch-name>` to create a new branch and
switch to it. `git checkout` is a versatile command with multiple use cases, while `git switch` was introduced only
to facilitate branch operations. The recommended way is to go with `git switch`, as it has a more intuitive syntax. In the
example above, I create a new branch called `bug-fix` and switch to it. After making some changes, I commit them.

```bash
git switch -c bug-fix
git commit -am "fixing a bug"
```

If I change my mind and decide to delete the branch, I have to switch back to `main` first and then run `git branch -d bug-fix`.
Note that, as a safety precaution, this will only work if the branch has been merged into another branch.
If you want to delete a branch that hasn't been merged yet, you can use `git branch -D <branch-name>`.
Deleting a remote branch is done by running `git push origin --delete <branch-name>`. Always be cautious when deleting branches,
as you may loose work that hasn't been merged yet.