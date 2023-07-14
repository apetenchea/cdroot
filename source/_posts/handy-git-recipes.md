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
I've put together some explanations of the most commonly used terminology and commands, as well as some recipes which
I often find myself using at work. I hope you'll find them useful too. For the record, at the time of this writing
I was using git version 2.37.0.

## Basics

### Commits

**A commit is a snapshot of all the tracked files in your project.** It contains the changes made since the previous commit,
along with metadata such as the commit author, timestamp, and a message describing the changes. Commits are organized sequentially,
each commit pointing to its parent commit. This is how git records the history of a repository. Think about it
in terms of inheritance, instead of time: a commit inherits the changes of its parent commit, and adds its own changes
on top of them. Everything in git is relative to something prior. More formally, commits are organized as a
[directed acyclic graph](https://en.wikipedia.org/wiki/Directed_acyclic_graph). This way, it is easy to traverse the history
of a repository and do all kinds of useful operations on it.

![Git commits](https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/handy-git-recipes/media/commits.png)

Every commit is identified by a unique hash (SHA-1), which is a 40-character hexadecimal string. When working with commits, it's rarely necessary to
reference them by their full identifier. You can pass in only a prefix (first 7 characters should be enough) and
git is smart enough to figure out the rest (as long as there exists only one commit with the given prefix). For example, let's consider
commit [dc2727cdfe357e4caf40f9c79c35d5232195ca45](https://github.com/apetenchea/cdroot/commit/dc2727cdfe357e4caf40f9c79c35d5232195ca45)
from this blog's [repository](https://github.com/apetenchea/cdroot). You can check the metadata associated with it
by running `git --no-replace-objects cat-file commit dc2727c`. The output is:

```
tree 2f3a693e39a75ae5e393c226c17895e6136d2d72
parent b200f511526c750833abf07dd5749aad7be1132b
author Alex Petenchea <email@gmail.com> 1682878857 +0300
committer Alex Petenchea <email@gmail.com> 1682878857 +0300
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
- Commit parent(s): The SHA-1 hash(es) of the commit parent(s). A commit can have multiple parents in the case of a merge commit (more on this later).
- Author: the name and email address of the person who authored the changes, along with the commit timestamp.
- Committer: the name and email address of the person who made the commit, along with the commit timestamp. This might be 
  different from the author if the changes were committed by another person, see [this commit for example](https://github.com/ArangoDB-Community/python-arango/commit/d7a0b560f62df370c162dbea08724c30a993c60c).
- GPG signature: this is optional, and can be used to verify the authenticity of the commit. It is generated using the author's
  private key, and can be verified using their public key.
- Commit message: the text of the commit message.

All that information is combined and hashed using the SHA-1 algorithm to produce a unique commit identifier. Just for fun, here's
how you can generate it yourself:
```shell
(printf "commit %s\0" $(git --no-replace-objects cat-file commit dc2727c | wc -c); git cat-file commit dc2727c) | sha1sum
```

For an explanation of the command above, check out [Carl Mäsak's gist](https://gist.github.com/masak/2415865). And finally,
to inspect the changes introduced with this commit, you can run `git show dc2727c`.  
Before committing, the usual workflow is to add your changes to the staging area.
```shell
git add .
git commit -m "explaining git"
```
The above was used to generate commit [a561329](https://github.com/apetenchea/cdroot/commit/a56132941d13867937334abc3de47765b49a36c8).
You may also use the shorthand `git commit -am "explaining git"`, which will automatically stage all changes before committing them.
However, note that this command will add and commit all the modified files, but not the *newly* created ones. Eventually,
you'll want to run `git push` to publish your changes to the remote repository.

### Branches

**A branch is a pointer to a commit.** When a new branch is created, it points to the same commit as the branch
it was created from. In other words, it is a "copy" of the current branch.
When you commit to a branch, the branch pointer is updated to point to the new commit. 
The default branch of a repository is usually called `main` or `master`.

![Git commits](https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/handy-git-recipes/media/branching.gif)

Creating a new branch is done by running `git branch <branch-name>`. To switch branches, run `git checkout <branch-name>`.
These two steps are usually done together, so there's a shorthand for it: `git checkout -b <branch-name>`. Alternatively, you can
use `git switch <branch-name>` to switch to an existing branch, or `git switch -c <branch-name>` to create a new branch and
switch to it. `git checkout` is a versatile command with multiple use cases, while `git switch` was introduced only
to facilitate branch operations. The recommended way is to go with `git switch`, as it has a more intuitive syntax. In the
example above, I create a new branch called `bug-fix` and switch to it. After making some changes, I commit them:

```shell
git switch -c bug-fix
git commit -am "fixing a bug"
```

If I change my mind and decide to delete the branch, I have to switch back to `main` first and then run `git branch -d bug-fix`.
Note that, as a safety precaution, this will only work if the branch has been merged into another branch.
If you want to delete a branch that hasn't been merged yet, you can use `git branch -D <branch-name>`.
Also, deleting a remote branch is done by running `git push origin --delete <branch-name>`. Always be cautious when deleting branches,
as you may lose work that hasn't been merged yet. One other thing, renaming a branch is easy: switch to it and run `git branch -m <new_branch_name>`.  

### Remotes

While working with git, you'll notice the term _remote_ being used everywhere. **A remote is a copy of the repository that is hosted elsewhere (on [Github](https://github.com/), for example)**.
You can have multiple remotes, and you can push and pull changes to and from them. The default remote is called `origin`, and it's
essentially a shorthand name for the remote repository's URL:

```shell
git clone git@github.com:apetenchea/cdroot.git
```

In this particular case, `origin` will point to `git@github.com:apetenchea/cdroot.git`. You can check what the remotes of
your repository point to by running `git remote -v`.  
You can always inspect the current state of your _local_ branch by running `git status`. If it's synchronized with the _remote_, you'll see
a message like this:

```
On branch bug-fix/issue-18919
Your branch is up to date with 'origin/bug-fix/issue-18919'.

nothing to commit, working tree clean
```

In the example above, `bug-fix/issue-18919` is the name of the _local branch_, and `origin/bug-fix/issue-18919` is the name of the
_remote branch_. Remote branches always reflect the state of the branch on the remote repository.
The naming convention is `<remote-name>/<branch-name>`.

#### pull

You can't work on remote branches directly, as they can just be updated from the remote.
However, you can _pull_ changes from them into your local branch. This is done by running `git pull <remote> <branch-name>`, or simply
`git pull` if you're already on the branch you want to pull changes into. This will fetch the changes from the remote branch and merge
them into your local branch.  

#### fetch

If you want to fetch the changes without switching to that branch, you can run `git fetch <remote> <branch-name>:<branch-name>`. This 
will bring the local representation of the remote branch into synchronization with the actual remote. Note that `git pull` is just a
shorthand for a fetch followed by an additional merge step.
When using fetch, one could, for example, create a new local copy of the remote branch by running `git fetch origin bug-fix/issue-18919:bug-fix/copy-of-issue-18919`.
Simply running `git fetch` without any additional arguments will fetch all the changes from all the remote branches.
If you're behind a slow network connection, this may take a while.  

#### push

Finally, `git push` is used to publish your local changes to the remote repository. If you're pushing a new branch, you'll have to
specify the remote branch name as well:
```shell
git push origin <local-branch-name>:<remote-branch-name>
```
Note that git forces you to incorporate the latest changes before pushing. This is to ensure that your push won't
overwrite any commits on the remote branch that aren't present in your local branch, which could lead to loss of work.
However, there may be times when you intentionally want to overwrite the remote branch, as for example, you may have
rewritten the commit history of your local branch. This is where `git push -f` comes into play, telling git to forcefully
push your commits, even if this means overwriting commits on the remote branch that aren't in your local branch.

As a side note, `push` does not necessarily imply that new commits will be added to the remote branch, but rather that
the remote branch will be updated. For example, `git push origin :bug-fix/issue-18919` will delete the branch from the
remote.

### Merging

**Merging is the process of combining two branches into one.** In git terms, the branch that receives the changes is called
the _target branch_, while the branch that is merged into it is called the _source branch_. Merging creates a special
commit called a _merge commit_. The special thing about it is that it has two parents:
the last commit of the target branch and the last commit of the source branch. The target branch is updated to point to the
merge commit, while the source branch remains unchanged.  
In the example below, we branch off _main_ to create a new branch called _bug-fix_. Then, each branch diverges, as we make
new commits: _c7b_ on _bug-fix_ and _037_ on _main_. Finally, we merge _bug-fix_ into _main_, which introduces a new commit
(_aaa_) that has both _c7b_ and _037_ as parents. Assuming _main_ is the current branch, this is the equivalent of running
`git merge bug-fix`.

![Git merge](https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/handy-git-recipes/media/merging.gif)

### Rebasing

**Rebasing is the process of moving a branch to a new base commit.** It essentially takes a set of commits and copies them
somewhere else. The new base commit is usually the tip of another branch. Rebasing is a powerful tool that can be used to
rewrite history, but it's also a dangerous tool, as it can easily lead to conflicts. Nevertheless, it makes your commit history
appear cleaner and more linear, which is why it's incorporated in the merging process by a lot of software projects.
Personally, I don't have a strong preference, as long as a consistent workflow is followed for the entire team.  
In the example below, we branch off _main_ and create a new branch called _bug-fix_. Similar to the merging example, each branch
diverges, but this time, before merging, we are going to rebase _bug-fix_ onto _main_. This means that we are going to copy the commits from _bug-fix_
and place them on top of _main_, which moves the point at which _bug-fix_ was branched to the last commit from _main_. After rebasing,
we can switch back to _main_ and merge _bug-fix_ into it. This will result in a fast-forward merge, as _bug-fix_ is now a direct descendant.
The resulting history is linear, appearing as if we were working on _main_ all along. Assuming that _bug-fix_ is the current branch, this is the equivalent
of running:

```shell
git rebase main
git switch main
git merge bug-fix
```

![Git rebase](https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/handy-git-recipes/media/rebasing.gif)

### Moving around

By moving around in git, I mean the ability to traverse up and down the commit tree that represents your project.

#### HEAD

You can think of `HEAD` as a pointer to the current commit. It's a symbolic name for the commit you're working on top of.
Normally, it points to the tip of the current branch, but it can also point to a commit, in case you have
checked out a specific commit instead of a branch. When `HEAD` refers to a commit, as opposed to a branch name,
it's said to be in a _detached state_.  
You can check what `HEAD` points to by inspecting the `.git/HEAD` file - it will either contain a reference to a
branch name or a commit hash.
```
git checkout main
cat .git/HEAD
ref: refs/heads/main

git checkout 7cc99c4
cat .git/HEAD
7cc99c460f1df70ba2a46bf120781ebc70a94cdd
```

If you just want to get the hash of the currently checked commit, regardless of the HEAD's state,
you can run `git rev-parse HEAD`. Nevertheless, the whole point of using `HEAD` is to avoid having to deal with
commit hashes. For example, let's take a look at the recent commit history of the
[python-arango](https://github.com/ArangoDB-Community/python-arango) project:
```
git log -5 | grep commit

commit a2f856af4851622156bac009a43506a7d756ab80
commit 0dc641e2ae296141bbf2e373b71a03e07a3ef87e
commit b82de8c4d525e08db4abe4ba9f804164123fa54c
commit f3307748337efa1c8a636e680a5a199be37e7be3
commit 8b09e077ea2155e5cd7a9cccb539b9ca57349155
```
As I'm writing this, `HEAD` points to the default branch, `main`, whose tip is the first commit in the list above.
Luckily, git provides relative refs, which are a very powerful way of referring to commits relative to another point
of reference, such as `HEAD` or a branch name (remember that a branch is just a pointer to a commit).

##### caret (^)

Each time you append a caret to a ref, you're telling git to traverse one commit up the commit tree. For example,
`HEAD^` is the parent of `HEAD`, `HEAD^^` is the grandparent of `HEAD`, and so on.
```
git rev-parse HEAD
a2f856af4851622156bac009a43506a7d756ab80

git rev-parse HEAD^
0dc641e2ae296141bbf2e373b71a03e07a3ef87e

git rev-parse HEAD^^
b82de8c4d525e08db4abe4ba9f804164123fa54c
```

You might be wondering what happens when you append a caret to a commit that has multiple parents. In this case,
you can specify which parent you want to traverse to. For example, `HEAD^2` is the second parent of `HEAD`. The default
is the first parent, so `HEAD^` is equivalent to `HEAD^1`.  
To wrap it up, you can use the caret to refer to any commit in the commit tree, as long as you know its position relative
to another commit or branch. This is very useful when you want to check out a specific commit. The following commands
are all equivalent and will check out the commit with hash `0dc641e`:
```
git checkout HEAD^
git checkout main^
git checkout a2f856a^
```

##### tilde (~)

You might have noticed that the caret is useful to refer to commits in the immediate vicinity of another commit or branch.
However, it might look awkward to use it when referring to commits that are further away. For example, if you want to refer to
the 5th parent of `HEAD`, you would have to write `HEAD^^^^^`. This is where the tilde comes in handy. It's similar to
the caret, but it's used to refer to the _nth_ ancestor of a commit. For example, `HEAD~5` is the 5th parent of `HEAD`.
The following examples all refer to the same commit:
```
git rev-parse HEAD^^^
f3307748337efa1c8a636e680a5a199be37e7be3

git rev-parse HEAD~3
f3307748337efa1c8a636e680a5a199be37e7be3

git rev-parse main~3
f3307748337efa1c8a636e680a5a199be37e7be3

git rev-parse a2f856a~3
f3307748337efa1c8a636e680a5a199be37e7be3
```

#### cherry-pick

I think this little command is one of the most underrated features of git. It allows you to pick any commits from anywhere
in the commit tree and apply them below your current location (HEAD). This is very useful when you want to apply just a
couple of commits from a branch to another. For example, let's say you have a branch called `feature` that contains
3 commits: `C2`, `C3` and `C4`. You want to apply `C3` and `C4` to your current branch, but not `C2`. You can do this
by running `git cherry-pick C3 C4`.

![Git cherry-pick](https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/handy-git-recipes/media/cherry-pick.gif)

Two popular use cases for `git cherry-pick` are:
- applying a hotfix to a release branch
- doing backports to older versions of your software

### Undoing changes

What if you realized that you made a mistake in your last commit? Or, you might have simply changed your mind about it.
As with most things in git, there are multiple ways to go about this.

#### reset

![Git rebase](https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/handy-git-recipes/media/reset.gif)

`git reset` is used to move the `HEAD` pointer to a specific commit. Assume you've made a mistake in your last commit,
and you want to go back to the previous commit. You can do this by running `git reset HEAD^`. This will move `HEAD` back one commit,
while keeping the working directory untouched, allowing you to make the necessary adjustments and commit them again.
This is equivalent to running `git reset --mixed HEAD^`, as it will un-stage the changes from the last commit,
but keep them in the working directory.
If you just want to move `HEAD` without affecting the staging area or the working directory,
you can run `git reset --soft HEAD^`.
The most destructive form is `git reset --hard HEAD^`, which will move `HEAD` to the parent of the current commit and
discard all changes from the current commit. This is useful when you want to completely get rid of a commit, but you
should be careful when using it, as it permanently deletes your modifications.  

As a general rule, it's ok to use `git reset` on branches that only you have seen or used, but it's not a good idea on
public branches where others may be collaborating with you. This is because `git reset` can rewrite the commit history,
which may cause conflicts and confusion for other collaborators.

To better illustrate the differences between the three forms of `git reset`, let's assume we have the following commit history
of the same [python-arango](https://github.com/ArangoDB-Community/python-arango) repository:
```
git log -2 | grep commit

commit a2f856af4851622156bac009a43506a7d756ab80
commit 0dc641e2ae296141bbf2e373b71a03e07a3ef87e
```

Suppose I modify `tester.sh` and stage it. Then, I modify `setup.py`, without staging it. This is what `git status` shows:
```
git status

On branch main
Your branch is up to date with 'origin/main'.

Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        modified:   tester.sh

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   setup.py
```

Finally, I commit my changes (note that only `tester.sh` will be included in the commit), `git commit -m "test"`:
```
[main da589a1] test
 1 file changed, 1 insertion(+), 1 deletion(-)
```

Then, `git status` shows the following:
```
On branch main
Your branch is ahead of 'origin/main' by 1 commit.
  (use "git push" to publish your local commits)

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   setup.py

no changes added to commit (use "git add" and/or "git commit -a")
```

##### --soft

Now, running `git reset --soft HEAD^` leaves the project in the same state as before I committed - `tester.sh`
staged and `setup.py` modified. See `git status` below:
```
On branch main
Your branch is up to date with 'origin/main'.

Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        modified:   tester.sh

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   setup.py
```

##### --mixed

`git reset --mixed HEAD^` leaves the repo in the same state as before I staged `tester.sh` - two modified files and nothing staged.
See `git status` below:
```
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   setup.py
        modified:   tester.sh

no changes added to commit (use "git add" and/or "git commit -a")
```

##### --hard

Finally, `git reset --hard HEAD^` leaves the repo in the exact same state as before I made any changes -
no staged files and no modified files, therefore erasing all my work.
See `git status` below:
```
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

#### revert

![Git rebase](https://raw.githubusercontent.com/apetenchea/cdroot/master/source/_posts/handy-git-recipes/media/revert.gif)

`git revert` provides a safer way to undo changes on public branches, without rewriting the commit history. Instead,
it undoes the changes of the specified commit, by creating a new commit. Therefore, it appends to the
commit history another commit which essentially cancels the diff introduced by the specified commit.
This is useful when you want to undo a commit that has already been pushed to a remote repository. By default,
it reverts the last commit, but you can specify any commit you want to revert using refs, just like with `git reset`.  
After committing something with the message "test", this is how the commit history looks after a `git revert`:
```
commit 7e3b51649987e13b294c84a561684c3c06a06387 (HEAD -> main)
Author: Alex Petenchea <email@gmail.com>
Date:   Wed Jul 12 21:45:33 2023 +0300

    Revert "test"

    This reverts commit 44859808807ef97d2d1f987acaf87d38dea6c28b.

commit 44859808807ef97d2d1f987acaf87d38dea6c28b
Author: Alex Petenchea <email@gmail.com>
Date:   Wed Jul 12 21:45:18 2023 +0300

    test
```

### Tagging

Branches are easily mutated. You can delete them, rename them, or move them around. This is why they are not a good
way to keep track of releases. Tags, on the other hand, are immutable. They're like snapshots of your project
at key moments in its history.  
To create a tag, you can use `git tag <tag_name>`, for example: `git tag v1.0.0`. By default,
it will create a tag for the current commit, but you can specify any commit you want using refs: `git tag v1.0.0 feature~2`.
There's mainly two reasons for why I find tags useful:
- it's easier to remember a tag name (such as `v1.0.0`) than a commit hash
- lots of release automation tools are based on tags

You can list all existing tags in your repository by running `git tag`. To push tags to the remote,
you can use `git push --tags`.

## Recipes

### Shallow cloning

Some repositories are huge, and you may not need the entire history of the project. For example, if you only plan to
compile [ArangoDB](https://github.com/arangodb/arangodb), you don't have to download the entire commit history.
You can speed up cloning substantially and use less disk space by using the `--single-branch` and `--depth`
parameters for the clone command as follows:
```
git clone --single-branch --depth 1 git@github.com:arangodb/arangodb.git
```
This is what's called a shallow clone. The `--single-branch` parameter tells git to only clone the default branch (in their case `devel`), and the
`--depth` parameter tells git how many commits to clone (in this example, only the last commit).

### Backports

ArangoDB (and many other software projects) continuously work towards new releases, while also maintaining older
versions. This means that bug fixes and new features are continuously being added to the `devel` branch, while
some (especially bug-fixes) also need to be back-ported to older versions.  
For example, take a look at this [pull request](https://github.com/arangodb/arangodb/pull/18958) which fixes a bug in
the `devel` branch. I had to backport this to 3 other branches: `3.11`, `3.10` and `3.9`.  
Once I completed my work on the `devel` branch, I have simply switched to the other branches and cherry-picked the
necessary commits, like this:
```
git switch 3.11
git cherry-pick e3de0d4fd2e2dd94ea0097939d1a918680536f6c  2b0b6166314b0482e43234d55d9917f5e8d3088c
```
For older branches, such as `3.9`, I had do some manual work to resolve conflicts, but it was still much faster than
having to re-implement the same fix 4 times.

### Interactive rebase

This is a really cool feature of git, which allows you to rewrite history in a very simple way. It's typically used
to clean up the mess before pushing to a remote repository: squashing commits, reordering commits, removing commits,
changing commit messages, etc. The "interactive" part means that git will open an interface for you to decide what to do.  
For example, you might have a couple of commits that you used for debugging, and you don't want to push them to the
remote repository. Or, you might have a couple of commits that are related to the same feature, and you want to squash
them into a single commit. I usually use it to squash _Work in progress_ commits.
```
git rebase -i HEAD~3
```
This will open an interface that looks like this:
```
pick b82de8c [DE-544] Retriable batch reads (#254)
pick 0dc641e [DE-544] Adjusting allowRetry implementation (#255)
pick a2f856a Adding ArangoSearch view creation test (#256)
```
The first commit is the oldest, and the last commit is the newest. You can reorder them by simply moving the lines
around. The first word on each line is the action that will be performed on that commit. The actions that I most
commonly use are: `pick`, `drop`, `squash` and `fixup`.  
For details, [checkout GitLab's tutorial](https://about.gitlab.com/blog/2020/11/23/keep-git-history-clean-with-interactive-rebase/)
on how to use interactive rebase.

### Ignoring files

Of course, there's the [.gitignore](https://git-scm.com/docs/gitignore) file for that. You can specify intentionally
untracked files or patterns that you want git to ignore. For example, you might want to ignore all files with the
`.log` extension, or all files in the `build` directory.  
However, sometimes you might want to ignore files without adding them to the `.gitignore` file. For example, you might
have a file that you want to ignore only on your machine, but not on other machines. In my case, I have some
build artifacts that I want to ignore, but I don't want to add them to the `.gitignore` file, because these are very
specific to my machine. I've added them to the `.git/info/exclude` file, inside hidden `.git` folder in my repository.
This file is similar to `.gitignore`, but it's not versioned. This means that it's not shared with other developers,
and it's not pushed to the remote repository.

## References

* [learngitbranching.js](https://learngitbranching.js.org/)
* [git-scm.com](https://git-scm.com/)