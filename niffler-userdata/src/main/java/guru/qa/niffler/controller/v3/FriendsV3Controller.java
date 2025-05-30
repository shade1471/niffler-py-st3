package guru.qa.niffler.controller.v3;

import guru.qa.niffler.model.IUserJson;
import guru.qa.niffler.service.UserService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;
import org.springframework.data.web.PagedModel;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/internal/v3/friends")
public class FriendsV3Controller {

  private static final Logger LOG = LoggerFactory.getLogger(FriendsV3Controller.class);

  private final UserService userService;

  @Autowired
  public FriendsV3Controller(UserService userService) {
    this.userService = userService;
  }

  @GetMapping("/all")
  public PagedModel<? extends IUserJson> friends(@RequestParam String username,
                                                 @PageableDefault Pageable pageable,
                                                 @RequestParam(required = false) String searchQuery) {
    return new PagedModel<>(
        userService.friends(username, pageable, searchQuery)
    );
  }
}
