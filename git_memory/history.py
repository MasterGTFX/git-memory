            # Calculate the diff from the parent of the oldest commit to the newest commit in the group.
            # If parent_of_group is None (initial commit group), diff is from empty tree to first_commit_in_group.
            first_commit_in_group = commit_group[0] # This is the newest commit in the group
            last_commit_in_group = commit_group[-1] # This is the oldest commit in the group

            # The parent of the group is the parent of the oldest commit in the group.
            # If the oldest commit is the initial commit, it has no parent.
            parent_of_group = last_commit_in_group.parents[0] if last_commit_in_group.parents else None

            # Calculate the diff from the parent of the oldest commit to the newest commit in the group.
            # If parent_of_group is None (initial commit group), diff is from empty tree to first_commit_in_group.
            diff = repo.git.diff(parent_of_group, first_commit_in_group.hexsha)

            with open(os.path.join(group_dir, "diff.patch"), "w", encoding="utf-8") as f:
                 f.write(diff)
