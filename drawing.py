from mcpi.minecraft import Minecraft
mc = Minecraft.create()

def fill_centered(x,y,z,w,h,l,block):
    for x1 in range(x-w,x+w):
        for y1 in range(y,y+h):
            for z1 in range(z-l,z+l):
                mc.setBlock(x1,y1,z1,block)
#    mc.setBlock(x-w,y,z-l,z+w,y+h,z+l,block)


def clear_around_player():
    player_pos = mc.player.getTilePos()
    fill_centered(player_pos.x, player_pos.y, player_pos.z, 40,40,40, 0)
    fill_centered(player_pos.x, player_pos.y-1, player_pos.z, 40,1,40, 2)

