# Step 7: Discogs Links and Actions

## Objective
Implement clickable Discogs links and actions for viewing releases and purchasing missing tracks.

## Tasks
- [ ] Generate proper Discogs URLs for releases
- [ ] Add [View] buttons that open Discogs in new tab
- [ ] Implement "Buy" links for missing physical formats
- [ ] Create search links for unmatched tracks
- [ ] Add link validation and error handling
- [ ] Implement deep linking to specific track positions
- [ ] Add link preview/tooltip functionality

## Link Types
- **Release View**: Direct link to Discogs release page
- **Buy Link**: Marketplace search for specific release
- **Search Link**: General search for artist + title
- **Track Position**: Deep link to specific track on release

## Acceptance Criteria
- [ ] All Discogs links open correctly in new tabs
- [ ] Links point to correct releases/tracks
- [ ] Buy links show relevant marketplace results
- [ ] Search links work for unmatched tracks
- [ ] Links include proper UTM tracking (optional)
- [ ] Error handling for invalid release IDs
