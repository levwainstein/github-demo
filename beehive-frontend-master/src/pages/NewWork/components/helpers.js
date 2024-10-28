export const backwardsSupportParseFromDescription = (description, title, profile) => {
    try {
        let parsedRepoName = null;
        let parsedRepoUrl = null;
        let a = description.split('**Github repo:** [');
        if (a.length > 0) {
            a = a[1];
            parsedRepoName = a.split(']')[0];
            const b = a.split(']')[1].split(')')[0];
            if (a.length > 0) {
                parsedRepoUrl = b.substring(1);
            }
        }
        let c = description.split('**Github branch for this task:** `');
        let parsedBranchName = null;
        if (c.length > 0) {
            c = c[1];
            parsedBranchName = c.split('`')[0];
            if (profile?.githubUser) {
                parsedBranchName = parsedBranchName.replace('{your_github_user}', profile.githubUser);
                parsedBranchName = parsedBranchName.replace('<your_github_user>', profile.githubUser);
            }
            
        }
        const parsedTitle = description.split('\n\n')[0];
        const branchSuffix = (title || parsedTitle).toLowerCase().replace(' ', '-');
        return { 
            name: parsedRepoName, 
            url: parsedRepoUrl,
            branch: parsedBranchName || `external/${profile?.githubUser || '<your_github_user>'}/${branchSuffix}`
        };
    } catch {
        return {
            name: null,
            url: null,
            branch: null
        };
    }
};
